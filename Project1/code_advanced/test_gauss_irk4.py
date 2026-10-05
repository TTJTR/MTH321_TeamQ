"""Independent checks for the optional two-stage implicit RK implementation."""

import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))

from model import benchmark, energy, exact_matrix, jacobian, rhs, unvectorize, vectorize  # noqa: E402
from gauss_irk4 import A, B, C, StageFailure, solve_fixed, stability_function  # noqa: E402


class GaussIRK4Tests(unittest.TestCase):
    def test_tableau_and_scalar_stability_function(self):
        np.testing.assert_allclose(A.sum(axis=1), C, atol=1e-15)
        self.assertAlmostEqual(float(B.sum()), 1.0)
        conditions = (B @ C, B @ C**2, B @ (A @ C), B @ C**3,
                      B @ (A @ C**2), B @ (C * (A @ C)), B @ (A @ A @ C))
        np.testing.assert_allclose(conditions, (1/2, 1/3, 1/6, 1/4,
                                                1/12, 1/8, 1/24), atol=1e-15)
        for z in (-8.0, -2.08, -0.1):
            result = solve_fixed(lambda t, y: z * y,
                                 lambda t, y: np.array([[z]]),
                                 np.array([1.0]), (0.0, 1.0), 1)
            self.assertAlmostEqual(float(result.y[-1, 0]), float(stability_function(z)), places=11)

    def test_a_stability_and_failure_of_l_stability(self):
        z = -np.geomspace(1e-3, 1e3, 40)[:, None] + 1j * np.linspace(-100, 100, 41)
        self.assertLessEqual(float(np.max(np.abs(stability_function(z)))), 1 + 1e-12)
        self.assertAlmostEqual(float(stability_function(-1e8)), 1.0, places=6)

    def test_fourth_order_on_full_matrix_solution(self):
        x0 = benchmark()
        exact = exact_matrix(2.0, x0)
        errors = []
        for n in (32, 64, 128):
            sol = solve_fixed(rhs, jacobian, vectorize(x0), (0.0, 2.0), n)
            errors.append(np.linalg.norm(unvectorize(sol.y[-1]) - exact, "fro"))
        orders = np.log2(np.asarray(errors[:-1]) / np.asarray(errors[1:]))
        self.assertTrue(np.all((orders > 3.7) & (orders < 4.2)), orders)

    def test_zero_singular_mode_in_rank_deficient_case(self):
        x0 = benchmark((0.0, 1.4, 3.0))
        sol = solve_fixed(rhs, jacobian, vectorize(x0), (0.0, 2.0), 32)
        self.assertLess(np.linalg.svd(unvectorize(sol.y[-1]), compute_uv=False)[-1], 1e-12)

    def test_newton_failure_is_reported(self):
        y0 = vectorize(benchmark())
        with self.assertRaises(StageFailure):
            solve_fixed(rhs, jacobian, y0, (0.0, 2.0), 4, max_newton=1)

    def test_reported_energy_and_tolerance_sensitivity(self):
        y0 = vectorize(benchmark())
        coarse = solve_fixed(rhs, jacobian, y0, (0.0, 2.0), 20)
        energies = np.array([energy(unvectorize(y)) for y in coarse.y])
        self.assertTrue(np.all(np.diff(energies) <= 1e-12))
        standard = solve_fixed(rhs, jacobian, y0, (0.0, 2.0), 128,
                               newton_tol=1e-12)
        tighter = solve_fixed(rhs, jacobian, y0, (0.0, 2.0), 128,
                              newton_tol=1e-14)
        exact = vectorize(exact_matrix(2.0, benchmark()))
        discretisation_error = np.linalg.norm(standard.y[-1] - exact)
        nonlinear_sensitivity = np.linalg.norm(standard.y[-1] - tighter.y[-1])
        self.assertLess(nonlinear_sensitivity, discretisation_error / 1000)


if __name__ == "__main__":
    unittest.main()
