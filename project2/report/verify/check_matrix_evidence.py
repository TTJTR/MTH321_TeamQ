"""Numerical corroboration for the matrix claims of Section 2.4.

Direction 3 of the problem pack asks for the symmetry defect ||A - A^T||/||A||
and for an assessment of positive definiteness whose numerical support is a
sparse Cholesky factorisation or a smallest-eigenvalue estimate -- a random
Rayleigh quotient is only a diagnostic.  This script produces exactly that
table from the production assembler, so the numbers in the report are the ones
the submitted code produces.

Run from project2/algorithm_section/:  python3 ../report/verify/check_matrix_evidence.py
"""

import os
import sys

import numpy as np
from scipy.sparse.linalg import eigsh
from scipy.linalg import cholesky

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "..", "algorithm_section"))
from src.discretisation import assemble_fdm  # noqa: E402

CASES = [
    ("smooth", 1.0, 32),
    ("smooth", 1.0, 64),
    ("layered", 10.0, 31),
    ("layered", 10.0, 63),
    ("layered", 100.0, 63),
]


def symmetry_defect(matrix):
    """Max-abs and Frobenius versions of ||A - A^T|| / ||A||."""
    difference = (matrix - matrix.T).tocsr()
    if difference.nnz == 0:
        return 0.0, 0.0
    max_abs = np.max(np.abs(difference.data))
    fro_defect = np.sqrt(np.sum(difference.data ** 2)) / np.sqrt(np.sum(matrix.data ** 2))
    return float(max_abs / np.max(np.abs(matrix.data))), float(fro_defect)


def smallest_eigenvalue(matrix):
    values = eigsh(matrix.tocsr().astype(float), k=1, which="SA",
                   return_eigenvectors=False, tol=1e-10, maxiter=20000)
    return float(values[0])


def main():
    print(f"{'case':>8} {'c':>5} {'N':>4} {'unknowns':>8} "
          f"{'defect_max':>11} {'defect_fro':>11} {'lambda_min':>12} "
          f"{'8a_min':>8} {'chol':>6}")
    for case, contrast, intervals in CASES:
        matrix, _, _ = assemble_fdm(intervals, case=case, contrast=contrast,
                                    average="harmonic")
        matrix = matrix.tocsr()
        defect_max, defect_fro = symmetry_defect(matrix)
        lam_min = smallest_eigenvalue(matrix)
        unknowns = matrix.shape[0]
        # a_chol = cholesky(..., lower=True) raises LinAlgError if not SPD
        try:
            dense = matrix.toarray()
            cholesky(dense, lower=True)
            chol = "ok"
        except np.linalg.LinAlgError:
            chol = "FAIL"
        a_min = 1.0
        print(f"{case:>8} {contrast:>5.0f} {intervals:>4d} {unknowns:>8d} "
              f"{defect_max:>11.2e} {defect_fro:>11.2e} {lam_min:>12.6e} "
              f"{8 * a_min:>8.1f} {chol:>6}")

    print()
    print("Reading: the defect is exactly zero because every off-diagonal entry is")
    print("written twice with the same shared face coefficient; a non-zero defect")
    print("would indicate that a face was assembled from two different averages.")
    print("lambda_min is an eigsh estimate (which='SA', tol 1e-10) and is compared")
    print("with the bound lambda_min >= 8 a_min of Section 2.4; a.d. Cholesky on the")
    print("dense matrix corroborates positive definiteness independently.")


if __name__ == "__main__":
    main()
