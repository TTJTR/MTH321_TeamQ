"""Two-stage Gauss--Legendre implicit Runge--Kutta method (order four).

Butcher, Numerical Methods for Ordinary Differential Equations, 3rd ed.
(Wiley, 2016), Chapter 3, Section 34.2, pp. 228--232.  This module
implements the coupled stages directly; no library ODE solver is called.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
RHS = Callable[[float, Array], Array]
Jacobian = Callable[[float, Array], Array]

C = np.array([0.5 - np.sqrt(3.0) / 6.0, 0.5 + np.sqrt(3.0) / 6.0])
A = np.array([[0.25, 0.25 - np.sqrt(3.0) / 6.0],
              [0.25 + np.sqrt(3.0) / 6.0, 0.25]])
B = np.array([0.5, 0.5])


class StageFailure(RuntimeError):
    """Coupled stage equations could not be solved."""


@dataclass
class Solution:
    t: Array
    y: Array
    nfev: int
    njev: int
    newton_iterations: int


def stability_function(z: complex | Array) -> complex | Array:
    """[2/2] Padé stability function for the two-stage Gauss method."""
    return (1 + z / 2 + z * z / 12) / (1 - z / 2 + z * z / 12)


def solve_fixed(f: RHS, jac: Jacobian, y0: Array,
                t_span: tuple[float, float], n_steps: int, *,
                newton_tol: float = 1e-12, max_newton: int = 20) -> Solution:
    """Solve on a uniform grid with damped Newton on the 2d stage system.

    The residual test is ||F||_inf <= tol*(1+||Y||_inf), where Y contains
    both stages.  RHS/Jacobian counts include trial evaluations in line search.
    """
    start, end = t_span
    if not end > start or n_steps < 1 or newton_tol <= 0 or max_newton < 1:
        raise ValueError("Invalid interval, step count, or Newton settings")
    y0 = np.asarray(y0, dtype=float)
    if y0.ndim != 1 or not np.all(np.isfinite(y0)):
        raise ValueError("Initial state must be a finite one-dimensional array")
    dim = y0.size
    identity = np.eye(dim)
    times = np.linspace(start, end, n_steps + 1)
    values = np.empty((n_steps + 1, dim))
    values[0] = y0
    nfev = njev = iterations = 0

    for k in range(n_steps):
        t, h, y = times[k], times[k + 1] - times[k], values[k]
        f0 = f(t, y)
        nfev += 1
        stages = np.stack((y + C[0] * h * f0, y + C[1] * h * f0))

        def residual(stage_values: Array) -> tuple[Array, Array]:
            nonlocal nfev
            rates = np.stack([f(t + C[i] * h, stage_values[i]) for i in range(2)])
            nfev += 2
            return stage_values - y - h * A @ rates, rates

        for it in range(max_newton + 1):
            defect, rates = residual(stages)
            norm = float(np.max(np.abs(defect)))
            target = newton_tol * (1 + float(np.max(np.abs(stages))))
            if np.isfinite(norm) and norm <= target:
                values[k + 1] = y + h * np.tensordot(B, rates, axes=(0, 0))
                iterations += it
                break
            if it == max_newton or not np.isfinite(norm):
                raise StageFailure(f"Stage Newton failed at step {k}")
            j0 = jac(t + C[0] * h, stages[0])
            j1 = jac(t + C[1] * h, stages[1])
            njev += 2
            system = np.block([[identity - h * A[0, 0] * j0, -h * A[0, 1] * j1],
                               [-h * A[1, 0] * j0, identity - h * A[1, 1] * j1]])
            try:
                correction = np.linalg.solve(system, -defect.reshape(2 * dim))
            except np.linalg.LinAlgError as exc:
                raise StageFailure(f"Singular stage Jacobian at step {k}") from exc
            correction = correction.reshape((2, dim))
            damping = 1.0
            while damping >= 1e-4:
                candidate = stages + damping * correction
                candidate_defect, _ = residual(candidate)
                if np.all(np.isfinite(candidate_defect)) and np.max(np.abs(candidate_defect)) < norm:
                    stages = candidate
                    break
                damping *= 0.5
            else:
                raise StageFailure(f"Stage line search failed at step {k}")
        if not np.all(np.isfinite(values[k + 1])):
            raise StageFailure(f"Nonfinite state at step {k}")
    return Solution(times, values, nfev, njev, iterations)
