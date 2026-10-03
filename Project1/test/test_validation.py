"""Independent checks of the model, methods, and project diagnostics."""

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "code"))

from model import (benchmark, energy, exact_matrix, frechet, jacobian,
                   matrix_rhs, orthogonality_defect, rhs, singular_values,
                   rotation, unvectorize, vectorize)
from solvers import StepFailure, solve_adaptive, solve_fixed


class PolarFlowValidation(unittest.TestCase):
    def setUp(self):
        self.x0 = benchmark()
        self.y0 = vectorize(self.x0)

    def test_column_major_jacobian_against_finite_difference(self):
        direction = np.arange(1, 10, dtype=float).reshape((3, 3), order="F") / 10
        epsilon = 1e-6
        numerical = (matrix_rhs(self.x0 + epsilon * direction) -
                     matrix_rhs(self.x0 - epsilon * direction)) / (2 * epsilon)
        self.assertLess(np.linalg.norm(numerical - frechet(self.x0, direction)), 1e-8)
        self.assertLess(np.linalg.norm(vectorize(numerical) -
                                       jacobian(0, self.y0) @ vectorize(direction)), 1e-8)

    def test_implicit_residual_jacobian_against_finite_difference(self):
        h, epsilon = 0.05, 1e-6
        direction = np.arange(1.0, 10.0) / 10.0

        def residual(w):
            return w - self.y0 - h * rhs(h, w)

        numerical = (residual(self.y0 + epsilon * direction) -
                     residual(self.y0 - epsilon * direction)) / (2 * epsilon)
        analytical = (np.eye(self.y0.size) - h * jacobian(h, self.y0)) @ direction
        self.assertLess(np.linalg.norm(numerical - analytical, ord=np.inf), 1e-8)

    def test_full_initial_and_equilibrium_spectra(self):
        initial = jacobian(0, self.y0)
        np.testing.assert_allclose(initial, initial.T, atol=1e-13)
        np.testing.assert_allclose(np.linalg.eigvalsh(initial),
                                   [-26, -14.16, -8.64, -7.44, -5.76,
                                    -4.88, -1.28, -0.72, 0.88], atol=1e-12)
        equilibrium = rotation(0.4) @ rotation(-0.7).T
        np.testing.assert_allclose(np.linalg.eigvalsh(jacobian(0, vectorize(equilibrium))),
                                   [-2] * 6 + [0] * 3, atol=1e-12)

    def test_exact_solution_and_independent_radau(self):
        self.assertLess(np.linalg.norm(exact_matrix(0, self.x0) - self.x0), 1e-14)
        oracle = solve_ivp(rhs, (0, 2), self.y0, method="Radau", jac=jacobian,
                           rtol=1e-12, atol=1e-14)
        self.assertTrue(oracle.success)
        self.assertLess(np.linalg.norm(unvectorize(oracle.y[:, -1]) -
                                       exact_matrix(2, self.x0)), 5e-12)

    def test_diagonal_scalar_sanity_case(self):
        initial = np.array([0.2, 1.4, 3.0])
        x0 = np.diag(initial)
        end = 0.7
        scalar = initial / np.sqrt(initial**2 + (1 - initial**2) * np.exp(-2 * end))
        exact = exact_matrix(end, x0)
        np.testing.assert_allclose(exact, np.diag(scalar), rtol=0, atol=1e-14)
        result = solve_fixed("rk4", rhs, jacobian, vectorize(x0), (0, end), 700)
        computed = unvectorize(result.y[-1])
        np.testing.assert_allclose(computed, np.diag(np.diag(computed)), rtol=0, atol=1e-14)
        self.assertLess(np.linalg.norm(computed - np.diag(scalar), "fro"), 1e-10)

    def test_fixed_step_orders(self):
        exact = exact_matrix(2, self.x0)
        for method, coarse, fine, lower, upper in (
            ("euler", 160, 320, 0.9, 1.1),
            ("implicit_euler", 160, 320, 0.9, 1.1),
            # Avoid the finest experiment grid, whose error is near round-off scale.
            ("rk4", 640, 1280, 3.7, 4.2),
        ):
            with self.subTest(method=method):
                errors = []
                for n in (coarse, fine):
                    sol = solve_fixed(method, rhs, jacobian, self.y0, (0, 2), n)
                    errors.append(np.linalg.norm(unvectorize(sol.y[-1]) - exact))
                observed = np.log2(errors[0] / errors[1])
                self.assertGreater(observed, lower)
                self.assertLess(observed, upper)

    def test_adaptive_controller_changes_step_and_respects_local_budget(self):
        for method in ("euler", "rk4", "implicit_euler"):
            with self.subTest(method=method):
                result = solve_adaptive(method, rhs, jacobian, self.y0, (0, 2), 0.15,
                                        atol=1e-8, rtol=1e-6)
                steps = np.diff(result.t)
                self.assertEqual(result.t[-1], 2.0)
                self.assertGreater(np.max(steps) / np.min(steps), 2)
                self.assertLessEqual(np.max(result.error_ratios), 1)
                # Independently check global error; a local budget is not a global bound.
                bound = 1e-5 if method == "rk4" else 1e-4
                self.assertLess(np.linalg.norm(unvectorize(result.y[-1]) -
                                               exact_matrix(2, self.x0)), bound)

    def test_tighter_adaptive_tolerance_reduces_global_error(self):
        exact = exact_matrix(2, self.x0)
        loose = solve_adaptive("rk4", rhs, jacobian, self.y0, (0, 2), 0.15,
                               atol=1e-5, rtol=1e-3)
        tight = solve_adaptive("rk4", rhs, jacobian, self.y0, (0, 2), 0.15,
                               atol=1e-10, rtol=1e-8)
        loose_error = np.linalg.norm(unvectorize(loose.y[-1]) - exact, "fro")
        tight_error = np.linalg.norm(unvectorize(tight.y[-1]) - exact, "fro")

        # The controller enforces a local normalized estimate, not a global
        # error bound. The exact matrix supplies the independent global check.
        self.assertEqual(loose.t[-1], 2)
        self.assertEqual(tight.t[-1], 2)
        self.assertLessEqual(np.max(loose.error_ratios), 1)
        self.assertLessEqual(np.max(tight.error_ratios), 1)
        self.assertGreater(len(tight.t), len(loose.t))
        self.assertLess(tight_error, loose_error / 100)

    def test_large_explicit_step_causes_singular_value_crossing(self):
        resolved = solve_fixed("euler", rhs, jacobian, self.y0, (0, 2), 40)
        coarse = solve_fixed("euler", rhs, jacobian, self.y0, (0, 2), 20)

        def has_crossing(solution):
            values = np.asarray([singular_values(unvectorize(row))
                                 for row in solution.y])
            return bool(np.any((values - 1) * (values[0] - 1) < -1e-9))

        self.assertFalse(has_crossing(resolved))  # h = 0.05
        self.assertTrue(has_crossing(coarse))     # h = 0.10
        resolved_error = np.linalg.norm(unvectorize(resolved.y[-1]) -
                                        exact_matrix(2, self.x0), "fro")
        coarse_error = np.linalg.norm(unvectorize(coarse.y[-1]) -
                                      exact_matrix(2, self.x0), "fro")
        self.assertGreater(coarse_error, resolved_error)

    def test_newton_failure_and_adaptive_retry_path(self):
        with self.assertRaisesRegex(StepFailure, "Newton iteration did not converge"):
            solve_fixed("implicit_euler", rhs, jacobian, self.y0, (0, 0.15), 1,
                        newton_tol=1e-11, max_newton=4)

        retried = solve_adaptive(
            "implicit_euler", rhs, jacobian, self.y0, (0, 0.15), 0.15,
            atol=1, rtol=0, newton_tol=1e-11, max_newton=4)
        retry_reference = solve_fixed(
            "implicit_euler", rhs, jacobian, self.y0, (0, 0.075), 2,
            newton_tol=1e-11, max_newton=4)

        self.assertEqual(retried.rejected, 1)
        np.testing.assert_allclose(retried.t, [0, 0.075, 0.15], rtol=0, atol=1e-15)
        np.testing.assert_allclose(retried.y[1], retry_reference.y[-1],
                                   rtol=0, atol=1e-14)
        # A converged Newton residual solves the discrete implicit equation; it
        # does not mean that the time-discrete state equals the exact ODE state.
        global_error = np.linalg.norm(unvectorize(retried.y[1]) -
                                      exact_matrix(0.075, self.x0), "fro")
        self.assertGreater(global_error, 1e-6)

    def test_resolved_singular_values_approach_one_without_crossing(self):
        for method in ("euler", "rk4", "implicit_euler"):
            with self.subTest(method=method):
                result = solve_fixed(method, rhs, jacobian, self.y0, (0, 2), 400)
                matrices = [unvectorize(row) for row in result.y]
                singular = np.asarray([singular_values(x) for x in matrices])
                self.assertTrue(np.all(np.diff(np.abs(singular - 1), axis=0) <= 1e-10))
                self.assertTrue(np.all((singular - 1) * (singular[0] - 1) >= -1e-10))
                self.assertTrue(np.all(np.diff([energy(x) for x in matrices]) <= 1e-12))

    def test_adaptive_can_finish_on_last_allowed_attempt(self):
        equilibrium = vectorize(np.eye(3))
        result = solve_adaptive("euler", rhs, jacobian, equilibrium, (0, 1), 1,
                                max_attempts=1)
        self.assertEqual(result.t[-1], 1.0)
        self.assertEqual(result.rejected, 0)

    def test_energy_and_rank_deficiency(self):
        velocity = matrix_rhs(self.x0)
        epsilon = 1e-6
        energy_derivative = (energy(self.x0 + epsilon * velocity) -
                             energy(self.x0 - epsilon * velocity)) / (2 * epsilon)
        self.assertAlmostEqual(energy_derivative,
                               -np.linalg.norm(velocity, "fro") ** 2, places=7)
        x_zero = benchmark((0, 1.4, 3))
        result = solve_fixed("rk4", rhs, jacobian, vectorize(x_zero), (0, 8), 800)
        matrices = [unvectorize(row) for row in result.y]
        energies = np.asarray([energy(x) for x in matrices])
        self.assertTrue(np.all(np.diff(energies) <= 1e-12))
        self.assertLess(max(singular_values(x)[-1] for x in matrices), 1e-12)
        self.assertAlmostEqual(orthogonality_defect(matrices[-1]), 1, places=8)
        np.testing.assert_allclose(singular_values(matrices[-1])[:2],
                                   [1, 1], rtol=0, atol=1e-6)
        left, initial_singular, right = np.linalg.svd(x_zero)
        partial_isometry = (left * (initial_singular > 1e-12)) @ right
        self.assertLess(np.linalg.norm(matrices[-1] - partial_isometry, "fro"), 1e-6)


if __name__ == "__main__":
    unittest.main()
