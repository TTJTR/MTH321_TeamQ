"""Sparse direct references and CG with explicit stopping and cost definitions."""
import time
import numpy as np
from scipy.sparse.linalg import LinearOperator, cg, eigsh, splu


def residuals(matrix, rhs, values):
    residual = rhs - matrix @ values
    relative = np.linalg.norm(residual) / max(np.linalg.norm(rhs), np.finfo(float).tiny)
    norm_a = float(np.max(np.asarray(abs(matrix).sum(axis=1))))
    denominator = norm_a * np.linalg.norm(values, np.inf) + np.linalg.norm(rhs, np.inf)
    backward = np.linalg.norm(residual, np.inf) / max(denominator, np.finfo(float).tiny)
    return dict(relative_residual=float(relative), backward_residual=float(backward))


def direct(matrix, rhs):
    started = time.perf_counter()
    factor = splu(matrix.tocsc(), permc_spec="COLAMD")
    factor_seconds = time.perf_counter() - started
    started = time.perf_counter()
    values = factor.solve(rhs)
    triangular_seconds = time.perf_counter() - started
    return values, dict(factor_seconds=factor_seconds, triangular_seconds=triangular_seconds,
                        direct_seconds=factor_seconds+triangular_seconds)


def conjugate_gradient(matrix, rhs, rtol=1e-12, jacobi=True, record=False):
    started = time.perf_counter()
    inverse_diagonal = 1 / matrix.diagonal()
    preconditioner = LinearOperator(matrix.shape, matvec=lambda v: inverse_diagonal*v) if jacobi else None
    setup_seconds = time.perf_counter() - started
    iterations = 0
    history = []
    rhs_norm = max(np.linalg.norm(rhs), np.finfo(float).tiny)

    def callback(values):
        nonlocal iterations
        iterations += 1
        if record:
            history.append(float(np.linalg.norm(rhs-matrix@values)/rhs_norm))

    started = time.perf_counter()
    values, info = cg(matrix, rhs, x0=np.zeros_like(rhs), rtol=rtol, atol=0,
                      maxiter=20000, M=preconditioner, callback=callback)
    if info != 0:
        raise RuntimeError(f"CG failed to meet tolerance: info={info}")
    refinements = 0
    for _ in range(3):
        explicit_residual = rhs - matrix @ values
        if np.linalg.norm(explicit_residual) <= 1.1 * rtol * rhs_norm:
            break
        correction, info = cg(
            matrix, explicit_residual, rtol=0, atol=0.1*rtol*rhs_norm,
            maxiter=20000, M=preconditioner,
            callback=lambda delta: callback(values+delta),
        )
        if info != 0:
            raise RuntimeError(f"CG residual correction failed: info={info}")
        values = values + correction
        refinements += 1
    seconds = time.perf_counter() - started
    metrics = residuals(matrix, rhs, values)
    if metrics["relative_residual"] > 1.1 * rtol:
        raise RuntimeError(f"Explicit CG residual exceeds tolerance: {metrics}")
    return values, dict(cg_iterations=iterations, cg_seconds=seconds,
                        cg_setup_seconds=setup_seconds, residual_refinements=refinements,
                        **metrics), history


def structure(matrix):
    skew = matrix - matrix.T
    off = matrix.copy()
    off.setdiag(0)
    off.eliminate_zeros()
    return dict(symmetry_relative=float(np.linalg.norm(skew.data)/np.linalg.norm(matrix.data)),
                min_diagonal=float(matrix.diagonal().min()),
                max_offdiagonal=float(off.data.max()), dof=matrix.shape[0], nnz=matrix.nnz)


def spectrum(matrix):
    initial = np.linspace(1, 2, matrix.shape[0])
    low, vl = eigsh(matrix, k=1, sigma=0, which="LM", tol=1e-10, v0=initial)
    high, vh = eigsh(matrix, k=1, which="LA", tol=1e-10, v0=initial)
    residual_low = np.linalg.norm(matrix@vl[:, 0]-low[0]*vl[:, 0]) / abs(low[0])
    residual_high = np.linalg.norm(matrix@vh[:, 0]-high[0]*vh[:, 0]) / abs(high[0])
    return dict(lambda_min=float(low[0]), lambda_max=float(high[0]),
                condition_estimate=float(high[0]/low[0]),
                eigen_residual_low=float(residual_low), eigen_residual_high=float(residual_high))
