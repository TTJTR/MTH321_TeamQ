import unittest
import numpy as np
from scipy.sparse.linalg import spsolve
from src.discretisation import (assemble_fdm, assemble_fem, forcing,
                                 error_norms, solution_grid, interface_diagnostics)


class Numerics(unittest.TestCase):
    def test_hand_matrix_and_interface_row(self):
        matrix, _, _ = assemble_fdm(3, "constant")
        expected = np.array([[4, -1, -1, 0], [-1, 4, 0, -1],
                             [-1, 0, 4, -1], [0, -1, -1, 4]]) * 9
        np.testing.assert_array_equal(matrix.toarray(), expected)
        matrix, _, _ = assemble_fdm(7, "layered", 10, "harmonic")
        row = (3-1)*6 + (3-1)
        self.assertAlmostEqual(matrix[row, row+6], -49*20/11)
        self.assertAlmostEqual(matrix[row, row], 49*(3+20/11))

    def test_independent_manufactured_forcing(self):
        step = 1e-4
        x = np.array([0.17, 0.43, 0.72])
        y = np.array([0.26, 0.61, 0.38])
        ux_right = np.pi*np.cos(np.pi*(x+step))*np.sin(np.pi*y)
        ux_left = np.pi*np.cos(np.pi*(x-step))*np.sin(np.pi*y)
        uy_top = np.pi*np.sin(np.pi*x)*np.cos(np.pi*(y+step))
        uy_bottom = np.pi*np.sin(np.pi*x)*np.cos(np.pi*(y-step))
        independent = -((1+x+step)*ux_right-(1+x-step)*ux_left)/(2*step)
        independent -= (1+x)*(uy_top-uy_bottom)/(2*step)
        np.testing.assert_allclose(independent, forcing(x, y), rtol=3e-8, atol=1e-7)

    def test_layered_exactness_and_matrix(self):
        for method, assemble, intervals in [("FDM", assemble_fdm, 15), ("FEM", assemble_fem, 16)]:
            for contrast in [1, 10, 100]:
                args = (intervals, "layered", contrast)
                matrix, rhs, meta = assemble(*args, **({"average": "harmonic"} if method == "FDM" else {}))
                values = solution_grid(spsolve(matrix, rhs), meta)
                self.assertLess(error_norms(values, "layered", contrast)["linf_nodal"], 1e-11)
                self.assertLess(interface_diagnostics(values, meta, method, contrast)["interface_flux_error"], 1e-9)
                np.testing.assert_allclose(matrix.toarray(), matrix.T.toarray(), atol=1e-13)
                self.assertGreater(np.linalg.eigvalsh(matrix.toarray())[0], 0)
                self.assertGreaterEqual(values.min(), -1e-12)
                self.assertLessEqual(values.max(), 1+1e-12)

    def test_smooth_convergence_and_quadrature(self):
        for assemble in [assemble_fdm, assemble_fem]:
            errors = []
            for intervals in [8, 16, 32]:
                matrix, rhs, meta = assemble(intervals)
                values = solution_grid(spsolve(matrix, rhs), meta)
                errors.append(error_norms(values)["l2_common"])
                doubled = error_norms(values, quadrature_order=8)["l2_common"]
                self.assertAlmostEqual(doubled, errors[-1], delta=1e-12)
            orders = np.log2(np.array(errors[:-1])/errors[1:])
            self.assertTrue(np.all((orders > 1.9) & (orders < 2.1)), orders)
        low, rhs_low, _ = assemble_fem(8, quadrature_order=5)
        high, rhs_high, _ = assemble_fem(8, quadrature_order=7)
        np.testing.assert_allclose(low.toarray(), high.toarray(), atol=1e-13)
        np.testing.assert_allclose(rhs_low, rhs_high, atol=1e-12)

    def test_fem_linear_patch(self):
        matrix, _, meta = assemble_fem(8, "constant")
        # Recover boundary forcing independently from affine exactness and full element assembly.
        from src.discretisation import mesh, geometry
        points, triangles, interior = mesh(8)
        vertices, determinant, gradients = geometry(points, triangles)
        affine = 2*points[:, 0] - 3*points[:, 1] + 1
        element_gradient = np.einsum("ta,tad->td", affine[triangles], gradients)
        np.testing.assert_allclose(element_gradient, np.tile([2, -3], (len(triangles), 1)), atol=1e-13)
        local = determinant[:, None, None]/2 * np.einsum("tid,tjd->tij", gradients, gradients)
        nodal_residual = np.bincount(triangles.ravel(),
            weights=np.einsum("tij,tj->ti", local, affine[triangles]).ravel(), minlength=len(points))
        self.assertLess(np.max(np.abs(nodal_residual[interior])), 1e-12)

    def test_arithmetic_comparison_and_parity(self):
        matrix, rhs, meta = assemble_fdm(15, "layered", 10, "arithmetic")
        values = solution_grid(spsolve(matrix, rhs), meta)
        self.assertGreater(error_norms(values, "layered", 10)["linf_nodal"], 1e-4)
        with self.assertRaises(ValueError):
            assemble_fdm(16, "layered")
        with self.assertRaises(ValueError):
            assemble_fem(15, "layered")

    def test_explicit_cg_residual_and_direct_agreement(self):
        from threadpoolctl import threadpool_limits
        from src.solvers import conjugate_gradient, direct
        with threadpool_limits(limits=1):
            matrix, rhs, _ = assemble_fdm(128)
            values, metrics, _ = conjugate_gradient(matrix, rhs)
            reference, _ = direct(matrix, rhs)
        self.assertLessEqual(metrics["relative_residual"], 1.1e-12)
        self.assertLess(np.max(np.abs(values-reference)), 1e-10)


if __name__ == "__main__":
    unittest.main()
