"""Independent verification of the Direction 3 production assemblers and solvers."""

import os
from pathlib import Path
import sys
import unittest

import numpy as np
from threadpoolctl import threadpool_limits

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from algorithm_section.src import discretisation as discret
from algorithm_section.src import solvers
from validate_interface import layered_model, layered_run, smooth_algebra
from validate_smooth import course_bank_check, input_checks, load_course_bank, patch_check, smooth_check


class SingleThreadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        limits = threadpool_limits(limits=1)
        limits.__enter__()
        cls.addClassCleanup(limits.__exit__, None, None, None)


class Direction3Validation(SingleThreadTests):
    def layered(self, n, contrast, rule):
        return layered_run(
            n, contrast, rule, discret.assemble_fdm, discret.assemble_fem,
            solvers.direct, discret.solution_grid,
        )

    def test_smooth_forcing_and_four_mesh_orders(self):
        rows = smooth_check(discret)
        for method in ("FDM", "FEM"):
            method_rows = [row for row in rows if row["method"] == method]
            self.assertEqual([row["N"] for row in method_rows], [16, 32, 64, 128])
            for norm in ("l2_nodal", "linf_nodal", "l2_common"):
                with self.subTest(method=method, norm=norm):
                    rate = method_rows[-1][f"fit_N32_to_128_{norm}"]
                    self.assertLess(abs(rate - 2), 0.1)

    def test_nonzero_dirichlet_indexing_and_spd(self):
        for row in patch_check(discret):
            with self.subTest(method=row["method"]):
                self.assertLess(row["boundary_linf"], 2e-14)
                self.assertLess(row["matrix_symmetry_linf"], 3e-12)
                self.assertGreater(row["lambda_min"], 0)

    def test_harmonic_and_fitted_fem_recover_layered_solution(self):
        for n, rule in ((31, "harmonic"), (32, "element_integral")):
            with self.subTest(rule=rule):
                row = self.layered(n, 10, rule)
                self.assertLess(row["linf_nodal"], 1e-11)
                self.assertLess(row["trace_flux_error"], 1e-9)
                self.assertLess(row["trace_flux_jump"], 1e-9)
                if rule == "harmonic":
                    self.assertLess(row["shared_flux_error"], 1e-9)
                    self.assertAlmostEqual(row["interface_weight"], 20 / 11)
                else:
                    self.assertEqual(row["fem_unaligned_triangles"], 0)
                    self.assertAlmostEqual(row["fem_material_integral_left"], 0.5)
                    self.assertAlmostEqual(row["fem_material_integral_right"], 5.0)

    def test_arithmetic_conserves_but_misses_physical_flux(self):
        row = self.layered(31, 10, "arithmetic")
        self.assertAlmostEqual(row["interface_weight"], 5.5)
        self.assertLess(row["dmp_excess"], 1e-12)
        self.assertLess(row["conservation_defect"], 1e-8)
        self.assertLess(row["trace_flux_jump"], 1e-9)
        self.assertGreater(row["shared_flux_error"], 0.1)
        self.assertGreater(row["linf_nodal"], 1e-3)

    def test_uniform_material_control(self):
        for n, rule in ((15, "arithmetic"), (15, "harmonic"), (16, "element_integral")):
            with self.subTest(rule=rule):
                row = self.layered(n, 1, rule)
                self.assertAlmostEqual(row["physical_flux"], -1.0)
                self.assertLess(row["linf_nodal"], 1e-11)
                self.assertLess(row["trace_flux_error"], 1e-9)

    def test_independent_conditioning_increases_with_mesh_and_contrast(self):
        estimates = {}
        for n in (15, 31):
            for contrast in (1, 10, 100):
                *_, low, high = layered_model(n, contrast, "harmonic")
                self.assertGreater(low, 0)
                estimates[n, contrast] = high / low
        for contrast in (1, 10, 100):
            self.assertGreater(estimates[31, contrast], estimates[15, contrast])
        for n in (15, 31):
            self.assertLess(estimates[n, 1], estimates[n, 10])
            self.assertLess(estimates[n, 10], estimates[n, 100])

    def test_cg_algebraic_error_and_explicit_residual(self):
        for method, assemble in (("FDM", discret.assemble_fdm), ("FEM", discret.assemble_fem)):
            rows = smooth_algebra(method, assemble, 32, solvers.direct, solvers.conjugate_gradient,
                                  (1e-6, 1e-9, 1e-12))
            self.assertLess(rows[0]["lu_backward_inf"], 2e-14)
            for row in rows[1:]:
                with self.subTest(method=method, rtol=row["rtol"]):
                    self.assertLessEqual(row["residual_rel2"], 1.1 * row["rtol"])
                    self.assertLess(row["linf_diff_over_lu_discretization"], 1e-3)

    def test_rejects_invalid_grid_parity_and_degenerate_coefficient(self):
        for assemble, invalid_n, valid_n in ((discret.assemble_fdm, 8, 7), (discret.assemble_fem, 7, 8)):
            for args in ((2,), (invalid_n, "layered"), (valid_n, "layered", 0)):
                with self.subTest(assembler=assemble.__name__, args=args), self.assertRaises(ValueError):
                    assemble(*args)


class CourseBankValidation(SingleThreadTests):
    def test_applies_four_course_bank_problems_to_both_assemblers(self):
        bank_path = os.environ.get("MTH321_TEST_BANK")
        if not bank_path:
            self.skipTest("Set MTH321_TEST_BANK to the course test_problem_bank.py")
        bank = load_course_bank(Path(bank_path))
        rows = course_bank_check(discret, bank)
        self.assertEqual(len(rows), 32)
        self.assertEqual({row["bank_case"] for row in rows}, {"P1", "P2", "P4", "P5"})


@unittest.skipUnless(os.environ.get("MTH321_STRICT_VALIDATION") == "1",
                     "Set MTH321_STRICT_VALIDATION=1 to run the defect regression checks")
class KnownDefectRegression(SingleThreadTests):
    def test_input_contract_and_extreme_face_coefficients(self):
        for row in input_checks(discret, solvers):
            with self.subTest(method=row["method"], probe=row["probe"]):
                self.assertEqual(row["status"], "PASS", row["actual"])

    def test_uniform_spectrum_matches_closed_form(self):
        for n in (15, 31, 63):
            matrix, _, _ = discret.assemble_fdm(n, "layered", 1, "harmonic")
            estimate = solvers.spectrum(matrix)
            angle = np.pi / (2 * n)
            with self.subTest(N=n):
                np.testing.assert_allclose(estimate["lambda_max"], 8 * n**2 * np.cos(angle)**2, rtol=1e-8)


if __name__ == "__main__":
    unittest.main()
