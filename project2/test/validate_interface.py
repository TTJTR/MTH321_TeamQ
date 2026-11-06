"""Independent resistance, material-integration and algebra audit (float64)."""

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np
from scipy.fft import dst, idst
from scipy.linalg import eigvalsh_tridiagonal, solveh_banded
from scipy.sparse import diags, eye, kron
from scipy.sparse.linalg import LinearOperator, cg, eigsh


def max_abs(values):
    return float(np.max(np.abs(values), initial=0.0))


def resistance_solution(x, contrast):
    flux = -1 / (0.5 + 0.5 / contrast)
    u = -flux * (np.minimum(x, 0.5) + np.maximum(x - 0.5, 0) / contrast)
    return u, flux


def layered_model(n, contrast, rule):
    """Independent reduced stencil, including exact FEM material integrals."""
    axis = np.arange(n + 1) / n
    if rule == "element_integral":
        # On these right triangles the diagonal coupling is zero. A horizontal
        # edge gets one half-strip conductivity from each of its two triangles.
        # A vertical edge on x=1/2 gets half the conductivity of each material.
        ax = np.where(np.arange(n) < n // 2, 1.0, contrast)
        ay = (ax[:-1] + ax[1:]) / 2
        scale = 1
    else:
        node_a = np.where(np.arange(n + 1) <= n // 2, 1.0, contrast)
        ax = node_a[:-1].copy()
        ax[n // 2] = 1 / (0.5 + 0.5 / contrast)
        if rule == "arithmetic":
            ax[n // 2] = (1 + contrast) / 2
        ay = node_a[1:-1]
        scale = n**2

    off_x = -scale * ax[1:-1]
    diag_x = scale * (ax[:-1] + ax[1:])
    diag_y = scale * ay
    tx = diags([off_x, diag_x, off_x], [-1, 0, 1], format="csr")
    ty = diags([-1.0, 2.0, -1.0], [-1, 0, 1], shape=tx.shape, format="csr")
    matrix = kron(tx, eye(n - 1), format="csr") + kron(diags(diag_y), ty, format="csr")

    exact, physical_flux = resistance_solution(axis, contrast)
    rhs = np.zeros((n - 1, n - 1))
    rhs[0, :] += scale * ax[0] * exact[0]
    rhs[-1, :] += scale * ax[-1] * exact[-1]
    rhs[:, 0] += diag_y * exact[1:-1]
    rhs[:, -1] += diag_y * exact[1:-1]

    # Sine eigenvectors diagonalize the y Laplacian. Its eigenvalues increase,
    # and each x block increases by a positive diagonal as the mode increases.
    mode_diags = diag_x[:, None] + diag_y[:, None] * (
        4 * np.sin(np.pi * np.arange(1, n) / (2 * n))**2
    )
    low = eigvalsh_tridiagonal(mode_diags[:, 0], off_x, select="i", select_range=(0, 0))[0]
    high = eigvalsh_tridiagonal(mode_diags[:, -1], off_x, select="i", select_range=(n - 2, n - 2))[0]
    transformed_rhs = dst(rhs, type=1, axis=1, norm="ortho")
    modes = np.empty_like(transformed_rhs)
    band = np.zeros((2, n - 1))
    band[1, :-1] = off_x
    for mode in range(n - 1):
        band[0] = mode_diags[:, mode]
        modes[:, mode] = solveh_banded(band, transformed_rhs[:, mode], lower=True)
    reference = idst(modes, type=1, axis=1, norm="ortho")
    return matrix, rhs.ravel(), reference.ravel(), exact, physical_flux, ax, ay, low, high


def residuals(matrix, rhs, values, lambda_lower):
    r = rhs - matrix @ values
    norm_a = float(np.max(np.asarray(abs(matrix).sum(axis=1))))
    denominator = norm_a * max_abs(values) + max_abs(rhs)
    return dict(
        residual_rel2=float(np.linalg.norm(r) / np.linalg.norm(rhs)),
        backward_inf=max_abs(r) / denominator,
        residual_over_lambda_lower=float(np.linalg.norm(r) / lambda_lower),
    )


def interface_metrics(n, contrast, rule, ax, ay, u, metadata, physical):
    if rule != "element_integral":
        qx = -n * ax[:, None] * np.diff(u, axis=0)
        qy = -n * ay[:, None] * np.diff(u[1:-1, :], axis=1)
        k = n // 2
        left, shared, right = qx[[k - 1, k, k + 1], 1:-1]
        ul = u[k, 1:-1] - left / (2 * n)
        ur = u[k + 1, 1:-1] + right / (2 * n * contrast)
        div = n * (np.diff(qx[:, 1:-1], axis=0) + np.diff(qy, axis=1))
        middle = np.abs(np.arange(1, n) / n - 0.5) <= 0.25
        near_center = np.argmin(np.abs(np.arange(1, n) / n - 0.5))
        return dict(
            shared_flux_error=max_abs(shared - physical),
            shared_flux_error_central_half=max_abs(shared[middle] - physical),
            shared_flux_error_nearest_midline=abs(shared[near_center] - physical),
            shared_flux_error_y=(np.argmax(np.abs(shared - physical)) + 1) / n,
            trace_flux_error=max(max_abs(left - physical), max_abs(right - physical)),
            trace_flux_jump=max_abs(left - right), trace_value_jump=max_abs(ul - ur),
            conservation_defect=max_abs(div),
        )

    vertices = metadata["points"][metadata["triangles"]]
    x = vertices[:, :, 0]
    left_triangles = x.max(axis=1) <= 0.5
    right_triangles = x.min(axis=1) >= 0.5
    unaligned = np.count_nonzero(~(left_triangles | right_triangles))
    edges = vertices[:, 1:] - vertices[:, :1]
    area = np.linalg.det(edges) / 2
    assert not unaligned and np.all(area > 0)
    assert np.count_nonzero(left_triangles) == np.count_nonzero(right_triangles) == n**2
    np.testing.assert_allclose([area[left_triangles].sum(), area[right_triangles].sum()],
                               [0.5, 0.5], rtol=1e-13, atol=0)
    interface_vertices = x == 0.5
    has_interface_edge = interface_vertices.sum(axis=1) == 2
    edge_y = (vertices[:, :, 1] * interface_vertices).sum(axis=1) / 2
    tri_u = u.ravel()[metadata["triangles"]]
    du = (tri_u[:, 1:] - tri_u[:, :1])[:, :, None]
    gx = np.linalg.solve(edges, du)[:, 0, 0]
    traces = []
    expected_midpoints = (np.arange(n) + 0.5) / n
    for side, material in ((left_triangles, 1), (right_triangles, contrast)):
        ids = np.flatnonzero(has_interface_edge & side)
        ids = ids[np.argsort(edge_y[ids])]
        np.testing.assert_allclose(edge_y[ids], expected_midpoints, atol=1e-14, rtol=0)
        traces.append(-material * gx[ids])
    return dict(
        trace_flux_error=max(max_abs(trace - physical) for trace in traces),
        trace_flux_jump=max_abs(traces[0] - traces[1]), trace_value_jump=0.0,
        fem_unaligned_triangles=int(unaligned), fem_interface_segments=n,
        fem_material_integral_left=float(area[left_triangles].sum()),
        fem_material_integral_right=float(contrast * area[right_triangles].sum()),
        fem_interface_y_coupling=float(ay[n // 2 - 1]),
    )


def layered_run(n, c, rule, assemble_fdm, assemble_fem, direct, solution_grid):
    fem = rule == "element_integral"
    if fem:
        matrix, rhs, metadata = assemble_fem(n, "layered", c)
    else:
        matrix, rhs, metadata = assemble_fdm(n, "layered", c, rule)
    expected, expected_rhs, reference, exact, physical, ax, ay, low, high = layered_model(n, c, rule)
    values, _ = direct(matrix, rhs)
    u = solution_grid(values, metadata)
    error = u - exact[:, None]
    boundary_error = max(max_abs(error[[0, -1], :]), max_abs(error[:, [0, -1]]))
    entries = matrix.tocoo()
    largest_offdiag = float(entries.data[entries.row != entries.col].max())
    lhs_rel = max_abs((matrix - expected).data) / max_abs(expected.data)
    rhs_rel = max_abs(rhs - expected_rhs) / max_abs(expected_rhs)
    independent_diff = max_abs(values - reference)
    dmp_excess = max(float(u.max() - exact.max()), float(exact.min() - u.min()), 0.0)
    reduced_row_slack = np.asarray(matrix.sum(axis=1)).ravel()
    assert lhs_rel < 2e-12 and rhs_rel < 2e-12 and independent_diff < 1e-10
    assert largest_offdiag <= 0 and low > 0 and dmp_excess < 1e-12
    assert reduced_row_slack.min() >= -2e-12 * max_abs(expected.data)
    # If the nodes are exact, a plain P1 chord still misses the kink.
    p1_exact_node_l2 = abs(physical * (1 - 1 / c)) * n**(-1.5) / (4 * np.sqrt(3))
    if not fem and rule == "harmonic":
        assert max_abs(error) < 1e-10
    return dict(
        method="FEM" if fem else "FDM", rule=rule, n=n, h=1 / n, dof=matrix.shape[0], contrast=c,
        interface_weight=None if fem else float(ax[n // 2]), physical_flux=physical,
        l2_nodal=float(np.linalg.norm(error[1:-1, 1:-1]) / n), linf_nodal=max_abs(error),
        exact_node_p1_l2_across_interface=0 if fem else p1_exact_node_l2,
        linf_dst_reference=max_abs(reference.reshape(n - 1, n - 1) - exact[1:-1, None]),
        linf_lu_vs_dst=independent_diff, boundary_linf=boundary_error,
        min_u=float(u.min()), max_u=float(u.max()), interior_min=float(values.min()),
        interior_max=float(values.max()), dmp_excess=dmp_excess,
        largest_offdiag=largest_offdiag, min_row_slack=float(reduced_row_slack.min()),
        symmetry_max_abs=max_abs((matrix - matrix.T).data), matrix_rel_maxdiff=lhs_rel,
        rhs_rel_maxdiff=rhs_rel, lambda_min=float(low), lambda_max=float(high), kappa2=float(high / low),
        **residuals(matrix, rhs, values, low),
        **interface_metrics(n, c, rule, ax, ay, u, metadata, physical),
    )


def conditioning(n, c, assemble_fdm, conjugate_gradient, spectrum, rtol):
    matrix, rhs, _ = assemble_fdm(n, "layered", c, "harmonic")
    _, _, _, _, _, _, _, low, high = layered_model(n, c, "harmonic")
    repo_eigs = spectrum(matrix)
    estimate = high / low
    relative_difference = abs(repo_eigs["condition_estimate"] - estimate) / estimate
    rng = np.random.default_rng(175)
    random_high = eigsh(matrix, k=1, which="LA", v0=rng.normal(size=matrix.shape[0]),
                        tol=1e-11, return_eigenvectors=False)[0]
    assert abs(random_high - high) / high < 1e-8
    if c == 1:
        analytic_high = 8 * n**2 * np.cos(np.pi / (2 * n))**2
        np.testing.assert_allclose(high, analytic_high, rtol=1e-13, atol=0)
    row = dict(n=n, h=1 / n, dof=matrix.shape[0], contrast=c, lambda_min=float(low),
               lambda_max=float(high), kappa2=float(estimate), rtol=rtol,
               random_start_lambda_max=float(random_high),
               repo_lambda_max=repo_eigs["lambda_max"], repo_kappa2=repo_eigs["condition_estimate"],
               repo_kappa_relative_difference=float(relative_difference),
               repo_eigen_residual_low=repo_eigs["eigen_residual_low"],
               repo_eigen_residual_high=repo_eigs["eigen_residual_high"])
    for jacobi, label in ((False, "plain"), (True, "jacobi")):
        _, info, _ = conjugate_gradient(matrix, rhs, rtol=rtol, jacobi=jacobi)
        row[label + "_iters"] = info["cg_iterations"]
        row[label + "_actual_residual"] = info["relative_residual"]
    return row


def smooth_algebra(method, assemble, n, direct, conjugate_gradient, tolerances):
    matrix, rhs, metadata = assemble(n, "smooth")
    solution, _ = direct(matrix, rhs)
    # Energy comparison against the unit-coefficient five-point matrix.
    # The aligned right-triangle FEM stiffness has the same stencil, unscaled.
    scale = n**2 if method == "FDM" else 1
    low = 8 * scale * np.sin(np.pi / (2 * n))**2
    high = 16 * scale * np.cos(np.pi / (2 * n))**2
    exact = (np.sin(np.pi * metadata["x"]) * np.sin(np.pi * metadata["y"]))[1:-1, 1:-1].ravel()
    disc = max_abs(solution - exact)
    record = dict(method=method, n=n, h=1 / n, dof=matrix.shape[0], lu_linf_nodal=disc,
                  lambda_lower=low, lambda_upper=high, kappa2_upper=high / low)
    diagonal = matrix.diagonal()
    jacobi = LinearOperator(matrix.shape, matvec=lambda x: x / diagonal)
    rtol = 1e-14
    tight, code = cg(matrix, rhs, M=jacobi, rtol=rtol, atol=0, maxiter=20000)
    tight_diff = max_abs(tight - solution)
    lu_check = residuals(matrix, rhs, solution, low)
    assert code == 0 and tight_diff < 1e-3 * disc
    rows = [dict(**record, solver="LU and independent tight CG", rtol=rtol,
                 linf_diff_vs_lu=tight_diff, linf_diff_over_lu_discretization=tight_diff / disc,
                 linf_nodal=max_abs(tight - exact),
                 **{f"lu_{key}": value for key, value in lu_check.items()},
                 **residuals(matrix, rhs, tight, low))]
    for rtol in tolerances:
        try:
            values, metrics, _ = conjugate_gradient(matrix, rhs, rtol=rtol)
        except RuntimeError as error:
            rows.append(dict(**record, solver="repo CG", rtol=rtol, failure=str(error)))
            if rtol >= 1e-12:
                raise
            continue
        difference = max_abs(values - solution)
        rows.append(dict(**record, solver="repo CG", rtol=rtol,
                         linf_diff_vs_lu=difference, linf_diff_over_lu_discretization=difference / disc,
                         linf_nodal=max_abs(values - exact), cg_iterations=metrics["cg_iterations"],
                         residual_refinements=metrics["residual_refinements"],
                         **residuals(matrix, rhs, values, low)))
    return rows


def write_rows(directory, name, rows):
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with (directory / name).open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algorithm-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    args = parser.parse_args()
    config = json.loads((args.algorithm_dir / "config.json").read_text(encoding="utf-8"))
    sys.path.insert(0, str(args.algorithm_dir.resolve()))
    from src.discretisation import assemble_fdm, assemble_fem, solution_grid
    from src.solvers import conjugate_gradient, direct, spectrum

    args.out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for rule in ("arithmetic", "harmonic", "element_integral"):
        grid_key = "layered_fem_intervals" if rule == "element_integral" else "layered_fdm_intervals"
        for n in config[grid_key]:
            rows.append(layered_run(n, 10, rule, assemble_fdm, assemble_fem, direct, solution_grid))
        # A homogeneous-material control uses the layered entry points and BCs.
        n = config[grid_key][0]
        rows.append(layered_run(n, 1, rule, assemble_fdm, assemble_fem, direct, solution_grid))
    write_rows(args.out_dir, "interface_layered.csv", rows)

    rows = [conditioning(n, c, assemble_fdm, conjugate_gradient, spectrum, config["cg_rtol"])
            for c in config["contrasts"] for n in config["conditioning_intervals"]]
    write_rows(args.out_dir, "interface_conditioning.csv", rows)

    rows = []
    for method, assemble in (("FDM", assemble_fdm), ("FEM", assemble_fem)):
        for n in config["smooth_intervals"]:
            tolerances = [config["cg_rtol"]]
            if n == 32:
                tolerances = config["tolerance_sweep"] + [1e-16]
            rows.extend(smooth_algebra(method, assemble, n, direct, conjugate_gradient, tolerances))
    write_rows(args.out_dir, "interface_algebra.csv", rows)
    print("Interface matrix, DST solution, flux, conditioning and algebra checks finished.")


if __name__ == "__main__":
    main()
