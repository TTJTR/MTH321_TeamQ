"""Three IVP methods and a step-doubling adaptive controller.

SciPy is deliberately absent here: these are the methods evaluated in the
project. SciPy's ``solve_ivp`` is used separately as an independent oracle.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray


Array = NDArray[np.float64]
RHS = Callable[[float, Array], Array]
Jacobian = Callable[[float, Array], Array]

# Controller bounds prevent abrupt changes in accepted trial length.
ADAPTIVE_SAFETY = 0.9
MIN_STEP_FACTOR = 0.2
MAX_STEP_FACTOR = 2.0
# Stop damped Newton before the trial correction becomes ineffective.
MIN_NEWTON_DAMPING = 1e-4


class StepFailure(RuntimeError):
    """A nonlinear solve or integration step could not be completed."""


@dataclass
class Solution:
    t: Array
    y: Array
    nfev: int
    njev: int
    newton_iterations: int
    rejected: int = 0
    error_ratios: Array | None = None


class _CountedProblem:
    def __init__(self, f: RHS, jac: Jacobian | None):
        self.f, self.jac = f, jac
        self.nfev = 0
        self.njev = 0

    def eval(self, t: float, y: Array) -> Array:
        self.nfev += 1
        return self.f(t, y)

    def derivative(self, t: float, y: Array) -> Array:
        if self.jac is None:
            raise ValueError("Implicit Euler needs an analytic Jacobian")
        self.njev += 1
        return self.jac(t, y)


def _one_step(method: str, p: _CountedProblem, t: float, y: Array, h: float,
              newton_tol: float, max_newton: int) -> tuple[Array, int]:
    if method == "euler":
        return y + h * p.eval(t, y), 0
    if method == "rk4":
        k1 = p.eval(t, y)
        k2 = p.eval(t + h / 2, y + h * k1 / 2)
        k3 = p.eval(t + h / 2, y + h * k2 / 2)
        k4 = p.eval(t + h, y + h * k3)
        return y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6, 0
    if method != "implicit_euler":
        raise ValueError(f"Unknown method: {method}")

    w = y.copy()
    for iteration in range(max_newton + 1):
        residual = w - y - h * p.eval(t + h, w)
        norm = np.linalg.norm(residual, ord=np.inf)
        # atol_F = rtol_F = newton_tol in the scale-aware rule from Section 2.
        target = newton_tol * (1 + np.linalg.norm(w, ord=np.inf))
        if np.isfinite(norm) and norm <= target:
            return w, iteration
        if iteration == max_newton or not np.isfinite(norm):
            break
        matrix = np.eye(y.size) - h * p.derivative(t + h, w)
        try:
            delta = np.linalg.solve(matrix, -residual)
        except np.linalg.LinAlgError as exc:
            raise StepFailure("Newton linear system is singular") from exc
        alpha = 1.0
        while alpha >= MIN_NEWTON_DAMPING:
            candidate = w + alpha * delta
            next_residual = candidate - y - h * p.eval(t + h, candidate)
            if np.all(np.isfinite(next_residual)) and np.linalg.norm(next_residual, ord=np.inf) < norm:
                w = candidate
                break
            alpha *= 0.5
        else:
            raise StepFailure("Newton line search did not reduce the residual")
    raise StepFailure("Newton iteration did not converge")


def solve_fixed(method: str, f: RHS, jac: Jacobian | None, y0: Array,
                t_span: tuple[float, float], n_steps: int, *,
                newton_tol: float = 1e-12, max_newton: int = 20) -> Solution:
    """Uniform grid, exact final endpoint; use for convergence measurements."""
    if n_steps < 1 or t_span[1] <= t_span[0]:
        raise ValueError("Require n_steps >= 1 and t_end > t_start")
    p = _CountedProblem(f, jac)
    times = np.linspace(*t_span, n_steps + 1)
    values = np.empty((n_steps + 1, y0.size))
    values[0] = y0
    iterations = 0
    for k in range(n_steps):
        values[k + 1], used = _one_step(method, p, times[k], values[k],
                                        times[k + 1] - times[k], newton_tol, max_newton)
        iterations += used
        if not np.all(np.isfinite(values[k + 1])):
            raise StepFailure("Nonfinite numerical state")
    return Solution(times, values, p.nfev, p.njev, iterations)


def solve_adaptive(method: str, f: RHS, jac: Jacobian | None, y0: Array,
                   t_span: tuple[float, float], initial_step: float, *,
                   atol: float = 1e-8, rtol: float = 1e-6,
                   newton_tol: float = 1e-12, max_newton: int = 20,
                   min_step: float = 1e-10, max_attempts: int = 100000) -> Solution:
    """Step doubling; accept the fine result and restart rejects from the old state."""
    if method not in ("euler", "rk4", "implicit_euler"):
        raise ValueError(f"Unknown method: {method}")
    t0, end = t_span
    if not end > t0 or initial_step <= 0 or atol <= 0 or rtol < 0:
        raise ValueError("Invalid interval, initial step, or tolerances")
    p = _CountedProblem(f, jac)
    order = 4 if method == "rk4" else 1
    t, y, h = float(t0), np.asarray(y0, dtype=float).copy(), float(initial_step)
    times, values, ratios = [t], [y.copy()], []
    rejected = iterations = 0
    for _ in range(max_attempts):
        if t >= end:
            break
        h = min(h, end - t)
        if h < min_step and end - t > min_step:
            raise StepFailure("Minimum step reached")
        failed_newton = False
        try:
            coarse, n1 = _one_step(method, p, t, y, h, newton_tol, max_newton)
            half, n2 = _one_step(method, p, t, y, h / 2, newton_tol, max_newton)
            fine, n3 = _one_step(method, p, t + h / 2, half, h / 2,
                                 newton_tol, max_newton)
            iterations += n1 + n2 + n3
            estimate = (fine - coarse) / (2**order - 1)
            scale = atol + rtol * np.maximum(np.abs(y), np.abs(fine))
            error = float(np.max(np.abs(estimate) / scale))
            if not np.isfinite(error):
                error = np.inf
        except StepFailure:
            error = np.inf
            failed_newton = True
        if error <= 1:
            t = min(t + h, end)
            y = fine
            times.append(t)
            values.append(y.copy())
            ratios.append(error)
            if t >= end:
                break
        else:
            rejected += 1
        if failed_newton:
            factor = 0.5  # Retry from the last accepted state, as in Algorithm 1.
        else:
            factor = MAX_STEP_FACTOR if error == 0 else float(np.clip(
                ADAPTIVE_SAFETY * error ** (-1 / (order + 1)),
                MIN_STEP_FACTOR, MAX_STEP_FACTOR))
        h *= factor
    else:
        raise StepFailure("Maximum adaptive step attempts exceeded")
    if t < end:
        raise StepFailure("Adaptive integration stopped before final time")
    return Solution(np.asarray(times), np.asarray(values), p.nfev, p.njev,
                    iterations, rejected, np.asarray(ratios))
