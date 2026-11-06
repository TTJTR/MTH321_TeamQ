"""Conservative FDM and conforming P1 FEM for Project 2, Direction 3.

FDM follows the existing interface-PINN baseline, with vectorised shared edges.
All grids use indexing='ij', C order, and y as the fastest coordinate.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.sparse import coo_matrix


def exact(x, y, case="smooth", contrast=10.0):
    if case == "smooth":
        return np.sin(np.pi * x) * np.sin(np.pi * y)
    if case == "constant":
        return np.zeros_like(x + y)
    return np.where(x <= 0.5, 2 * contrast * x / (1 + contrast),
                    (2 * x + contrast - 1) / (1 + contrast))


def forcing(x, y, case="smooth"):
    if case != "smooth":
        return np.zeros_like(x + y)
    return (2 * np.pi**2 * (1 + x) * np.sin(np.pi * x) * np.sin(np.pi * y)
            - np.pi * np.cos(np.pi * x) * np.sin(np.pi * y))


def coefficient(x, case="smooth", contrast=10.0):
    if case == "smooth":
        return 1 + x
    if case == "constant":
        return np.ones_like(x)
    return np.where(x < 0.5, 1.0, contrast)


def grid(intervals):
    if not isinstance(intervals, (int, np.integer)) or intervals < 3:
        raise ValueError("N must be an integer >= 3")
    axis = np.linspace(0, 1, intervals + 1)
    x, y = np.meshgrid(axis, axis, indexing="ij")
    return x, y


def assemble_fdm(intervals, case="smooth", contrast=10.0, average="arithmetic"):
    if case not in {"smooth", "layered", "constant"} or not np.isfinite(contrast) or contrast <= 0:
        raise ValueError("Unsupported case or nonpositive contrast")
    if average not in {"arithmetic", "harmonic"}:
        raise ValueError("Unsupported face average")
    if case == "layered" and intervals % 2 == 0:
        raise ValueError("Layered FDM requires odd N")
    x, y = grid(intervals)
    n = intervals - 1
    a = coefficient(x, case, contrast)
    boundary = exact(x, y, case, contrast)
    if average == "harmonic":
        ax_lo, ax_hi = np.minimum(a[:-1, :], a[1:, :]), np.maximum(a[:-1, :], a[1:, :])
        ay_lo, ay_hi = np.minimum(a[:, :-1], a[:, 1:]), np.maximum(a[:, :-1], a[:, 1:])
        ax = 2 * ax_lo / (1 + ax_lo / ax_hi)
        ay = 2 * ay_lo / (1 + ay_lo / ay_hi)
    else:
        ax = (a[:-1, :] + a[1:, :]) / 2
        ay = (a[:, :-1] + a[:, 1:]) / 2
    east, west = ax[1:, 1:-1], ax[:-1, 1:-1]
    north, south = ay[1:-1, 1:], ay[1:-1, :-1]
    scale = intervals**2
    index = np.arange(n * n).reshape(n, n)
    horizontal_left, horizontal_right = index[:-1, :].ravel(), index[1:, :].ravel()
    vertical_low, vertical_high = index[:, :-1].ravel(), index[:, 1:].ravel()
    rows = np.concatenate([index.ravel(), horizontal_left, horizontal_right,
                           vertical_low, vertical_high])
    cols = np.concatenate([index.ravel(), horizontal_right, horizontal_left,
                           vertical_high, vertical_low])
    values = scale * np.concatenate([
        (east + west + north + south).ravel(), -east[:-1, :].ravel(),
        -east[:-1, :].ravel(), -north[:, :-1].ravel(), -north[:, :-1].ravel(),
    ])
    matrix = coo_matrix((values, (rows, cols)), shape=(n*n, n*n)).tocsr()
    rhs = forcing(x[1:-1, 1:-1], y[1:-1, 1:-1], case).copy()
    rhs[0, :] += scale * west[0, :] * boundary[0, 1:-1]
    rhs[-1, :] += scale * east[-1, :] * boundary[-1, 1:-1]
    rhs[:, 0] += scale * south[:, 0] * boundary[1:-1, 0]
    rhs[:, -1] += scale * north[:, -1] * boundary[1:-1, -1]
    return matrix, rhs.ravel(), dict(x=x, y=y, boundary=boundary, ax=ax, ay=ay)


def mesh(intervals):
    x, y = grid(intervals)
    points = np.column_stack([x.ravel(), y.ravel()])
    ids = np.arange((intervals + 1)**2).reshape(intervals + 1, intervals + 1)
    p00, p10 = ids[:-1, :-1].ravel(), ids[1:, :-1].ravel()
    p01, p11 = ids[:-1, 1:].ravel(), ids[1:, 1:].ravel()
    triangles = np.concatenate([
        np.column_stack([p00, p10, p11]), np.column_stack([p00, p11, p01]),
    ])
    interior = ids[1:-1, 1:-1].ravel()
    return points, triangles, interior


def triangle_quadrature(order=5):
    """Tensor Gauss rule under the Duffy map; weights sum to 1/2."""
    nodes, weights = leggauss(order)
    nodes, weights = (nodes + 1) / 2, weights / 2
    r, s = np.meshgrid(nodes, nodes, indexing="ij")
    wr, ws = np.meshgrid(weights, weights, indexing="ij")
    barycentric = np.column_stack([
        ((1-r)*(1-s)).ravel(), r.ravel(), ((1-r)*s).ravel(),
    ])
    return barycentric, (wr * ws * (1-r)).ravel()


def geometry(points, triangles):
    vertices = points[triangles]
    first = vertices[:, 1] - vertices[:, 0]
    second = vertices[:, 2] - vertices[:, 0]
    determinant = first[:, 0]*second[:, 1] - first[:, 1]*second[:, 0]
    gradients = np.stack([
        np.column_stack([vertices[:, 1, 1]-vertices[:, 2, 1],
                         vertices[:, 2, 0]-vertices[:, 1, 0]]),
        np.column_stack([vertices[:, 2, 1]-vertices[:, 0, 1],
                         vertices[:, 0, 0]-vertices[:, 2, 0]]),
        np.column_stack([vertices[:, 0, 1]-vertices[:, 1, 1],
                         vertices[:, 1, 0]-vertices[:, 0, 0]]),
    ], axis=1) / determinant[:, None, None]
    return vertices, determinant, gradients


def assemble_fem(intervals, case="smooth", contrast=10.0, quadrature_order=5):
    if case not in {"smooth", "layered", "constant"} or not np.isfinite(contrast) or contrast <= 0:
        raise ValueError("Unsupported case or nonpositive contrast")
    if case == "layered" and intervals % 2:
        raise ValueError("Layered FEM requires even N for interface alignment")
    points, triangles, interior = mesh(intervals)
    vertices, determinant, gradients = geometry(points, triangles)
    barycentric, weights = triangle_quadrature(quadrature_order)
    samples = np.einsum("qa,tad->tqd", barycentric, vertices)
    integrated_a = determinant * (coefficient(samples[:, :, 0], case, contrast) @ weights)
    local_matrix = integrated_a[:, None, None] * np.einsum("tid,tjd->tij", gradients, gradients)
    local_rhs = determinant[:, None] * np.einsum(
        "tq,qa,q->ta", forcing(samples[:, :, 0], samples[:, :, 1], case),
        barycentric, weights,
    )
    rows = np.broadcast_to(triangles[:, :, None], local_matrix.shape).ravel()
    cols = np.broadcast_to(triangles[:, None, :], local_matrix.shape).ravel()
    size = len(points)
    full = coo_matrix((local_matrix.ravel(), (rows, cols)), shape=(size, size)).tocsr()
    full.eliminate_zeros()
    load = np.bincount(triangles.ravel(), weights=local_rhs.ravel(), minlength=size)
    is_boundary = np.ones(size, dtype=bool)
    is_boundary[interior] = False
    boundary_ids = np.flatnonzero(is_boundary)
    values = exact(points[:, 0], points[:, 1], case, contrast)
    rhs = load[interior] - full[interior][:, boundary_ids] @ values[boundary_ids]
    matrix = full[interior][:, interior].tocsr()
    x, y = grid(intervals)
    return matrix, rhs, dict(x=x, y=y, boundary=values.reshape(x.shape),
                             points=points, triangles=triangles, interior=interior,
                             gradients=gradients)


def solution_grid(values, metadata):
    result = metadata["boundary"].copy()
    result[1:-1, 1:-1] = values.reshape(result.shape[0]-2, result.shape[1]-2)
    return result


def error_norms(solution, case="smooth", contrast=10.0, quadrature_order=6):
    intervals = solution.shape[0] - 1
    x, y = grid(intervals)
    error = solution - exact(x, y, case, contrast)
    points, triangles, _ = mesh(intervals)
    vertices, determinant, _ = geometry(points, triangles)
    barycentric, weights = triangle_quadrature(quadrature_order)
    samples = np.einsum("qa,tad->tqd", barycentric, vertices)
    interpolated = solution.ravel()[triangles] @ barycentric.T
    sampled_error = interpolated - exact(samples[:, :, 0], samples[:, :, 1], case, contrast)
    integrated = np.sum(determinant * (sampled_error**2 @ weights))
    return dict(l2_nodal=float(np.linalg.norm(error[1:-1, 1:-1])/intervals),
                linf_nodal=float(np.max(np.abs(error))), l2_common=float(np.sqrt(integrated)))


def fdm_fluxes(solution, metadata):
    intervals = solution.shape[0] - 1
    qx = -metadata["ax"] * np.diff(solution, axis=0) * intervals
    qy = -metadata["ay"] * np.diff(solution, axis=1) * intervals
    divergence = intervals * (qx[1:, 1:-1]-qx[:-1, 1:-1]
                              + qy[1:-1, 1:]-qy[1:-1, :-1])
    return qx, qy, divergence


def interface_diagnostics(solution, metadata, method, contrast):
    intervals = solution.shape[0] - 1
    physical = -2 * contrast / (1 + contrast)
    if method == "FDM":
        qx, _, divergence = fdm_fluxes(solution, metadata)
        left = intervals // 2
        qleft, qright = qx[left-1, 1:-1], qx[left+1, 1:-1]
        qinterface = qx[left, 1:-1]
        # Extrapolate the pure-material edge slope by h/2 to the interface.
        uleft = solution[left, 1:-1] - qleft / (2*intervals)
        uright = solution[left+1, 1:-1] + qright / (2*intervals*contrast)
        return dict(
            interface_flux_error=float(np.max(np.abs(qinterface-physical))),
            reconstructed_flux_jump=float(np.max(np.abs(qleft-qright))),
            reconstructed_value_jump=float(np.max(np.abs(uleft-uright))),
            balance_linf=float(np.max(np.abs(divergence))),
        )
    gradients = np.einsum("ta,tad->td", solution.ravel()[metadata["triangles"]],
                          metadata["gradients"])
    triangles = metadata["triangles"]
    vertices = metadata["points"][triangles]
    on_interface = np.isclose(vertices[:, :, 0], 0.5)
    adjacent = on_interface.sum(axis=1) == 2
    centroids = vertices.mean(axis=1)
    traces = []
    for side, a in [(0, 1.0), (1, contrast)]:
        selected = adjacent & ((centroids[:, 0] < 0.5) if side == 0 else (centroids[:, 0] > 0.5))
        indices = np.flatnonzero(selected)
        midpoints = np.sum(vertices[indices, :, 1] * on_interface[indices], axis=1) / 2
        order = np.argsort(midpoints)
        traces.append(-a * gradients[indices[order], 0])
    return dict(interface_flux_error=float(max(np.max(np.abs(q-physical)) for q in traces)),
                reconstructed_flux_jump=float(np.max(np.abs(traces[0]-traces[1]))),
                reconstructed_value_jump=0.0, balance_linf=None)
