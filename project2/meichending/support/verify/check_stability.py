"""Reproduces the two numbers quoted in Remark 2.12 of the report.

Claim audited: does  A_h >= a_min * A_h^(1)  (Loewner order) imply the ENTRYWISE
inequality  0 <= A_h^{-1} <= a_min^{-1} (A_h^{(1)})^{-1}  ?
Both matrices in question are symmetric M-matrices, so the question is whether
the Loewner order and the entrywise order agree for inverses of M-matrices.

Answer: no.  The script also reports the quantity that DOES hold,
||A_h^{-1}||_inf, against the sharp constant- coefficient bound 1/(8 a_min).
"""
import numpy as np


def assemble_1d(a, n):
    """Vertex-centred 5-point (here 3-point) operator, h = 1/(n+1)."""
    h = 1.0 / (n + 1)
    x = np.arange(1, n + 1) * h
    face = np.empty(n + 1)
    face[0] = 0.5 * (a(0.0) + a(x[0]))
    for i in range(n - 1):
        face[i + 1] = 0.5 * (a(x[i]) + a(x[i + 1]))
    face[n] = 0.5 * (a(x[-1]) + a(1.0))
    A = np.zeros((n, n))
    for i in range(n):
        A[i, i] = (face[i] + face[i + 1]) / h ** 2
        if i > 0:
            A[i, i - 1] = -face[i] / h ** 2
        if i < n - 1:
            A[i, i + 1] = -face[i + 1] / h ** 2
    return A, h


def assemble_2d(a, n):
    """Same operator on the n x n interior grid, a = a(x) only."""
    h = 1.0 / (n + 1)
    x = np.arange(1, n + 1) * h
    av = np.array([a(t) for t in x])
    N = n * n
    A = np.zeros((N, N))
    for i in range(n):
        for j in range(n):
            k = i * n + j
            aE = av[i] if i + 1 < n else a(1.0)
            aW = av[i] if i > 0 else a(0.0)
            A[k, k] = (aE + aW + 2 * av[i]) / h ** 2
            if i > 0:
                A[k, (i - 1) * n + j] = -aW / h ** 2
            if i < n - 1:
                A[k, (i + 1) * n + j] = -aE / h ** 2
            if j > 0:
                A[k, k - 1] = -av[i] / h ** 2
            if j < n - 1:
                A[k, k + 1] = -av[i] / h ** 2
    return A, h


if __name__ == "__main__":
    n = 63
    a = lambda t: 1.0 + 9.0 * np.sin(np.pi * t) ** 2      # a_min = 1
    A, h = assemble_1d(a, 63)
    A1, _ = assemble_1d(lambda t: 1.0, n)
    amin = 1.0
    ratio = np.linalg.inv(A) / (np.linalg.inv(A1) / amin)
    print("counterexample  a(x) = 1 + 9 sin^2(pi x),  n = %d, a_min = 1" % n)
    print("  max_kl  (A_h^-1)_kl / (a_min^-1 (A_h^(1))^-1)_kl = %.4f" % ratio.max())
    print("  entrywise inequality 0 <= A_h^-1 <= a_min^-1 (A_h^(1))^-1 : %s"
          % ("HOLDS" if ratio.max() <= 1 + 1e-12 else "FAILS"))

    print()
    print("sharp constant 1/(8 a_min) vs measured ||A_h^-1||_inf")
    for label, f, npts, dim in (("a = 1 + x   (1D)", lambda t: 1.0 + t, 63, 1),
                                ("a = 1 + x   (2D)", lambda t: 1.0 + t, 14, 2)):
        A, _ = (assemble_1d if dim == 1 else assemble_2d)(f, npts)
        w = np.linalg.inv(A).dot(np.ones(A.shape[0]))
        print("  %s  n = %3d :  ||A^-1||_inf = %.4f   bound = %.4f   ratio = %.3f"
              % (label, npts, w.max(), 0.125, w.max() / 0.125))
