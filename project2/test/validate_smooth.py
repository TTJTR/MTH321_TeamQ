"""Independent Role 5 smooth diffusion, course bank and input checks.

Usage: python -B validate_smooth.py --algorithm PATH --bank PATH --out PATH
Use --strict to return exit 1 when the input/scale contract probes find failures.
The fixed snapshot and the original course bank are supplied as input.
"""

import argparse
import csv
import importlib.util
import os
import sys
import warnings
from pathlib import Path
from unittest.mock import patch

if __name__ == "__main__":
    for variable in ("OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "OMP_NUM_THREADS"):
        os.environ[variable] = "1"

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import eigsh, spsolve


INTERVALS = (16, 32, 64, 128)


def grid(n):
    axis = np.arange(n + 1) / n
    return np.meshgrid(axis, axis, indexing="ij")


def absmax(array):
    return float(np.max(np.abs(array), initial=0.0))


def common_p1_l2(values, exact):
    """Integrate over square cells split at v=t, using independent Gauss loops."""
    n = values.shape[0] - 1
    x, y = grid(n)
    x, y = x[:-1, :-1], y[:-1, :-1]
    u00, u10, u01, u11 = (
        values[:-1, :-1], values[1:, :-1], values[:-1, 1:], values[1:, 1:]
    )
    nodes, weights = leggauss(8)
    integral = 0.0
    for t, wt in zip((nodes + 1) / 2, weights / 2):
        for z, wz in zip((nodes + 1) / 2, weights / 2):
            v_lo, v_hi = t * z, t + (1 - t) * z
            lower = (1 - t) * u00 + (t - v_lo) * u10 + v_lo * u11
            upper = (1 - v_hi) * u00 + (v_hi - t) * u01 + t * u11
            e_lo = lower - exact(x + t / n, y + v_lo / n)
            e_hi = upper - exact(x + t / n, y + v_hi / n)
            integral += wt * wz * (t * np.sum(e_lo**2) + (1 - t) * np.sum(e_hi**2))
    return float(np.sqrt(integral) / n)


def solve(d, matrix, rhs, metadata, exact, n):
    values = spsolve(matrix.tocsc(), rhs, use_umfpack=False)
    solution = d.solution_grid(values, metadata)
    x, y = grid(n)
    reference = exact(x, y)
    error = solution - reference
    np.testing.assert_array_equal(solution[1:-1, 1:-1].ravel(), values)
    boundary = (x == 0) | (x == 1) | (y == 0) | (y == 1)
    residual = rhs - matrix @ values
    return solution, {
        "dof": len(values),
        "l2_nodal": np.linalg.norm(error[1:-1, 1:-1]) / n,
        "linf_nodal": absmax(error),
        "l2_common": common_p1_l2(solution, exact),
        "residual_linf": absmax(residual),
        "relative_residual_l2": np.linalg.norm(residual) / np.linalg.norm(rhs),
        "boundary_linf": absmax(error[boundary]),
    }


def add_rates(rows, names, eligible=True):
    for name in names:
        errors = np.array([row[name] for row in rows])
        fit = np.polyfit(np.log([row["h"] for row in rows[1:]]), np.log(errors[1:]), 1)[0] if eligible else ""
        for i, row in enumerate(rows):
            row[f"rate_{name}"] = np.log2(errors[i - 1] / errors[i]) if i and eligible else ""
            row[f"fit_N32_to_128_{name}"] = fit


def smooth_check(d, bank=None):
    def exact(x, y):
        return np.sin(np.pi * x) * np.sin(np.pi * y)

    rng = np.random.default_rng(321)
    x, y = rng.uniform(size=(2, 256))
    # Derivative of the physical flux by complex step, with no subtraction
    # of nearly equal flux samples. Independent of the production RHS algebra.
    step = 1e-25
    xj, yj = x + 1j * step, y + 1j * step
    qx = -(1 + xj) * np.pi * np.cos(np.pi * xj) * np.sin(np.pi * y)
    qy = -(1 + x) * np.pi * np.sin(np.pi * x) * np.cos(np.pi * yj)
    rhs_defect = absmax((qx.imag + qy.imag) / step - d.forcing(x, y))
    assert rhs_defect < 2e-13
    np.testing.assert_allclose(d.exact(x, y), exact(x, y), atol=2e-15, rtol=0)
    np.testing.assert_allclose(d.coefficient(x), 1 + x, atol=2e-15, rtol=0)
    if bank is not None:
        np.testing.assert_allclose(d.forcing(x, y), bank.P4.forcing(x, y), atol=2e-13, rtol=0)
        np.testing.assert_allclose(exact(x, y), bank.P4.exact(x, y), atol=2e-15, rtol=0)
        np.testing.assert_allclose(1 + x, bank.P4.coefficient(x, y), atol=2e-15, rtol=0)

    output = []
    for method, assemble in (("FDM", d.assemble_fdm), ("FEM", d.assemble_fem)):
        rows = []
        for n in INTERVALS:
            matrix, rhs, meta = assemble(n)
            solution, norms = solve(d, matrix, rhs, meta, exact, n)
            team_common = d.error_norms(solution)["l2_common"]
            n_dof = matrix.shape[0]
            v0 = np.linspace(1, 2, n_dof)
            low, vector = eigsh(matrix, k=1, sigma=0, which="LM", v0=v0, tol=1e-10)
            symmetric_defect = absmax((matrix - matrix.T).data)
            eigen_defect = np.linalg.norm(matrix @ vector[:, 0] - low[0] * vector[:, 0]) / low[0]
            assert symmetric_defect < 1e-13 and low[0] > 0 and eigen_defect < 1e-8
            assert norms["boundary_linf"] < 2e-15 and norms["relative_residual_l2"] < 1e-11
            assert abs(norms["l2_common"] - team_common) < 2e-13
            xg, yg = grid(n)
            boundary = (xg == 0) | (xg == 1) | (yg == 0) | (yg == 1)
            rows.append({
                "method": method, "N": n, "h": 1 / n, **norms,
                "rhs_complex_step_abs_defect": rhs_defect,
                "boundary_abs_from_zero": absmax(solution[boundary]),
                "l2_common_repo_abs_defect": abs(norms["l2_common"] - team_common),
                "matrix_symmetry_linf": symmetric_defect,
                "lambda_min": low[0], "eigenpair_relative_residual": eigen_defect,
            })
        add_rates(rows, ("l2_nodal", "linf_nodal", "l2_common"))
        for row in rows[1:]:
            assert 1.9 < row["rate_l2_common"] < 2.1
        output.extend(rows)
    return output


def use_problem(d, exact, forcing, coefficient):
    """Supply course fields to the actual assembler via its module callbacks."""
    return patch.multiple(
        d,
        exact=lambda x, y, *args: exact(x, y),
        forcing=lambda x, y, *args: forcing(x, y),
        coefficient=lambda x, *args: coefficient(x, np.zeros_like(x)),
    )


def course_bank_check(d, bank):
    output = []
    for problem_id in ("P1", "P2", "P4", "P5"):
        problem = getattr(bank, problem_id)
        for method, assemble in (("FDM", d.assemble_fdm), ("FEM", d.assemble_fem)):
            rows = []
            with use_problem(d, problem.exact, problem.forcing, problem.coefficient):
                for n in INTERVALS:
                    solution, norms = solve(d, *assemble(n), problem.exact, n)
                    centre = solution[n // 2, n // 2]
                    reference = {16: 1.65200, 32: 1.64954}.get(n, "") if problem_id == "P5" and method == "FDM" else ""
                    if reference != "":
                        assert abs(centre - reference) < 5e-6
                    assert norms["boundary_linf"] < 2e-15
                    assert norms["relative_residual_l2"] < 1e-11
                    rows.append({
                        "bank_case": problem_id, "method": method, "N": n, "h": 1 / n,
                        **norms, "centre_value": centre, "centre_bank_rounded": reference,
                    })
            # P2 reproduces the nodal values on this mesh. P1 interpolants of
            # its quadratic trace still have O(h^2) continuous error.
            add_rates(rows, ("l2_nodal", "linf_nodal"), eligible=problem_id != "P2")
            add_rates(rows, ("l2_common",))
            if problem_id == "P2":
                assert max(row["linf_nodal"] for row in rows) < 2e-12
            else:
                assert 1.9 < rows[-1]["fit_N32_to_128_l2_nodal"] < 2.1
            assert 1.9 < rows[-1]["fit_N32_to_128_l2_common"] < 2.1
            output.extend(rows)
    return output


def independent_affine_system(n, method, exact):
    """Build the entire small system, including boundary columns, by loops."""
    size = (n + 1)**2
    full = np.zeros((size, size))
    load = np.zeros(size)
    ids = np.arange(size).reshape(n + 1, n + 1)
    x, y = grid(n)
    points = np.column_stack((x.ravel(), y.ravel()))
    if method.startswith("FDM"):
        for i in range(1, n):
            for j in range(1, n):
                k = ids[i, j]
                load[k] = -2.0
                for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)):
                    low, high = sorted((1 + i / n, 1 + a / n))
                    if method == "FDM harmonic":
                        conductance = 2 / (1 / low + 1 / high)
                    else:
                        conductance = 1 + (i + a) / (2 * n)
                    full[k, ids[a, b]] = -n**2 * conductance
                    full[k, k] += n**2 * conductance
    else:
        area = 0.5 / n**2
        for i in range(n):
            for j in range(n):
                for nodes in ((ids[i, j], ids[i+1, j], ids[i+1, j+1]),
                              (ids[i, j], ids[i+1, j+1], ids[i, j+1])):
                    vertices = points[list(nodes)]
                    basis = np.column_stack((np.ones(3), vertices))
                    grads = np.linalg.solve(basis, np.eye(3))[1:]
                    mean_a = 1 + np.mean(vertices[:, 0])
                    full[np.ix_(nodes, nodes)] += (area * mean_a) * (grads.T @ grads)
                    load[list(nodes)] += -2 * area / 3
    interior = ids[1:-1, 1:-1].ravel()
    boundary = np.setdiff1d(ids.ravel(), interior)
    rhs = load[interior] - full[np.ix_(interior, boundary)] @ exact(x, y).ravel()[boundary]
    return full[np.ix_(interior, interior)], rhs


def patch_check(d):
    def exact(x, y):
        return 3 + 2 * x - y

    def forcing(x, y):
        return np.full_like(x + y, -2.0)

    def coefficient(x, y):
        return 1 + x

    # At N=8 coordinates are dyadic. Arithmetic FDM and conforming P1 FEM
    # are exact for this affine field; harmonic FDM uses a different face rule.
    n = 8
    output = []
    with use_problem(d, exact, forcing, coefficient):
        for method, assemble in (
            ("FDM arithmetic", d.assemble_fdm),
            ("FDM harmonic", lambda n: d.assemble_fdm(n, average="harmonic")),
            ("FEM", d.assemble_fem),
        ):
            matrix, rhs, meta = assemble(n)
            expected_matrix, expected_rhs = independent_affine_system(n, method, exact)
            solution, norms = solve(d, matrix, rhs, meta, exact, n)
            face_defect = ""
            if method.startswith("FDM"):
                axis = np.arange(n + 1) / n
                west, east = 1 + axis[:-1], 1 + axis[1:]
                ax = 2 / (1 / west + 1 / east) if method == "FDM harmonic" else 1 + axis[:-1] + 0.5 / n
                face_defect = max(absmax(meta["ax"] - ax[:, None]), absmax(meta["ay"] - (1 + axis[:, None])))
                assert face_defect < 1e-14
            actual = matrix.toarray()
            matrix_defect = absmax(actual - expected_matrix)
            rhs_defect = absmax(rhs - expected_rhs)
            independent_values = np.linalg.solve(expected_matrix, expected_rhs)
            independent_solve_defect = absmax(solution[1:-1, 1:-1].ravel() - independent_values)
            assert matrix_defect < 3e-12 and rhs_defect < 3e-12 and independent_solve_defect < 1e-12
            if method != "FDM harmonic":
                assert norms["linf_nodal"] < 2e-13
            np.linalg.cholesky(actual)
            output.append({
                "method": method, "N": n, **norms,
                "independent_matrix_linf_defect": matrix_defect,
                "independent_rhs_linf_defect": rhs_defect,
                "independent_dense_solve_linf_defect": independent_solve_defect,
                "shared_face_linf_defect": face_defect,
                "matrix_symmetry_linf": absmax(actual - actual.T),
                "lambda_min": np.linalg.eigvalsh(actual)[0],
            })
    return output


def input_checks(d, solvers):
    rows = []
    for method, assemble in (("FDM", d.assemble_fdm), ("FEM", d.assemble_fem)):
        rejected = [
            ("unknown case", (8, "typo"), {}),
            ("N=2", (2,), {}),
            ("noninteger N", (8.5,), {}),
            ("wrong layered parity", (8 if method == "FDM" else 7, "layered"), {}),
            ("c=0", (7 if method == "FDM" else 8, "layered", 0.0), {}),
            ("c=-1", (7 if method == "FDM" else 8, "layered", -1.0), {}),
            ("c=-inf", (7 if method == "FDM" else 8, "layered", -np.inf), {}),
            ("c=nan", (7 if method == "FDM" else 8, "layered", np.nan), {}),
            ("c=+inf", (7 if method == "FDM" else 8, "layered", np.inf), {}),
            ("unknown average", (7,), {"average": "typo"}) if method == "FDM"
            else ("quadrature_order=0", (8,), {"quadrature_order": 0}),
        ]
        for label, args, kwargs in rejected:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", RuntimeWarning)
                try:
                    matrix, rhs, meta = assemble(*args, **kwargs)
                except ValueError as error:
                    result = f"ValueError: {error}"
                    passed = True
                else:
                    result = (
                        f"returned; nonfinite matrix entries={np.count_nonzero(~np.isfinite(matrix.data))}; "
                        f"nonfinite rhs={np.count_nonzero(~np.isfinite(rhs))}; "
                        f"nonfinite boundary array={np.count_nonzero(~np.isfinite(meta['boundary']))}"
                    )
                    passed = False
            rows.append(dict(method=method, probe=label, status="PASS" if passed else "FAIL", actual=result))

    for method, assemble, n in (
        ("FDM arithmetic", d.assemble_fdm, 7),
        ("FDM harmonic", lambda *args: d.assemble_fdm(*args, average="harmonic"), 7),
        ("FEM", d.assemble_fem, 8),
    ):
        for contrast in (1e-200, 1e200):
            with np.errstate(over="ignore", invalid="ignore", under="ignore"):
                matrix, rhs, meta = assemble(n, "layered", contrast)
            if method.startswith("FDM"):
                pure = meta["ax"][5, 3]
            else:
                row = (6 - 1) * (n - 1) + (3 - 1)
                pure = matrix[row, row] / 4
            nonfinite = np.count_nonzero(~np.isfinite(matrix.data))
            zero_diagonals = np.count_nonzero(matrix.diagonal() == 0.0)
            passed = (nonfinite == 0 and zero_diagonals == 0 and np.isfinite(rhs).all()
                      and abs(pure / contrast - 1) < 2e-14)
            rows.append(dict(
                method=method, probe=f"c={contrast:.0e}", status="PASS" if passed else "FAIL",
                actual=f"pure-right conductance {pure:.17g}; nonfinite matrix entries={nonfinite}; zero diagonals={zero_diagonals}",
            ))
    # Small diagnostic outside the supported N>=3 assembly path. A diagonal
    # SPD matrix is valid input to a generic structural inspection routine.
    diagonal = csr_matrix([[4.0]])
    try:
        result = solvers.structure(diagonal)
    except ValueError as error:
        rows.append(dict(method="structure", probe="diagonal SPD [[4]]", status="FAIL", actual=f"ValueError: {error}"))
    else:
        passed = result["min_diagonal"] == 4.0 and result["dof"] == 1 and result["nnz"] == 1
        rows.append(dict(method="structure", probe="diagonal SPD [[4]]", status="PASS" if passed else "FAIL", actual=str(result)))
    return rows


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def load_course_bank(path):
    if not path.is_file():
        raise FileNotFoundError(f"Course bank not found: {path}")
    spec = importlib.util.spec_from_file_location("course_test_problem_bank", path.resolve())
    if spec is None or spec.loader is None:
        raise ValueError(f"Expected a Python course bank file: {path}")
    bank = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bank)
    # Current assemblers evaluate a(x) only. Guard the use of the four
    # original bank coefficients at y=0 in the callback adapter.
    x, y = grid(7)
    for problem in (bank.P1, bank.P2, bank.P4, bank.P5):
        np.testing.assert_array_equal(problem.coefficient(x, y), problem.coefficient(x, np.zeros_like(x)))
    return bank


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--algorithm", type=Path, required=True)
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(args.algorithm.resolve()))
    from src import discretisation, solvers

    bank = load_course_bank(args.bank)
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Course bank forcing self-check, worst relative difference {bank.verify_bank():.12e}")
    write_csv(args.out / "smooth_convergence.csv", smooth_check(discretisation, bank))
    write_csv(args.out / "smooth_course_bank.csv", course_bank_check(discretisation, bank))
    write_csv(args.out / "smooth_affine_patch.csv", patch_check(discretisation))
    probes = input_checks(discretisation, solvers)
    write_csv(args.out / "smooth_input_checks.csv", probes)
    for probe in probes:
        if probe["status"] == "FAIL":
            print(f"FAIL {probe['method']} {probe['probe']}: {probe['actual']}")
    failures = sum(row["status"] == "FAIL" for row in probes)
    print(f"Smooth convergence, four applicable bank problems, and affine system checks completed. Input probes: {len(probes) - failures} pass, {failures} fail.")
    return int(args.strict and failures > 0)


if __name__ == "__main__":
    raise SystemExit(main())
