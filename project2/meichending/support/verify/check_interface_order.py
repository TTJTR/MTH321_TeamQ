"""Reproduces the one-dimensional interface-order numbers behind Section 2.2 and
Appendix A, Audit 1 of the Project 2 report.

The layered benchmark  a = a_L (x < 1/2), a = a_R (x > 1/2), f = 0,
u(0) = 0, u(1) = 1  has the exact solution

    u*(x) = 2 c x / (1 + c)                 for x <= 1/2
    u*(x) = (2 x + c - 1) / (1 + c)         for x >= 1/2      with c = a_R / a_L

and the exact flux  J* = -2 a_L a_R / (a_L + a_R)  across every face.

With an odd number of intervals the interface lies between two columns.  Then:

  * harmonic (resistor-in-series) face coefficients reproduce u* at every node
    to round-off and the numerical flux equals J* on every face;
  * arithmetic face coefficients give a nodal error that is first order in h,
    and the one-dimensional chain has the closed form quoted in the report,
    whose leading relative flux error is h (a_L - a_R)^2 / (a_L + a_R)^2.

Run:  python3 verify/check_interface_order.py
"""

import numpy as np

AL, AR = 1.0, 10.0
C = AR / AL
J_STAR = -2.0 * AL * AR / (AL + AR)


def a_of(x):
    return AL if x < 0.5 else AR


def u_exact(x):
    if x <= 0.5:
        return 2.0 * C * x / (1.0 + C)
    return (2.0 * x + C - 1.0) / (1.0 + C)


def face_coefficient(left_medium, right_medium, rule):
    """Conductance of the face between two adjacent nodes."""
    if left_medium is None or right_medium is None:
        return None
    if left_medium == right_medium:
        return left_medium
    return 0.5 * (left_medium + right_medium) if rule == "arith" \
        else 2.0 * left_medium * right_medium / (left_medium + right_medium)


def solve_1d(n_intervals, rule):
    """Vertex-centred conservative scheme; returns nodal values and face fluxes."""
    h = 1.0 / n_intervals
    m = (n_intervals - 1) // 2          # interface between columns m and m+1
    nodes = n_intervals - 1
    # material of each column (node i has coordinate i*h, i = 1..n_intervals-1)
    medium = [a_of(i * h) for i in range(n_intervals + 1)]

    def face(i):
        """face i lies between column i and column i+1, i = 0..n_intervals-1"""
        return face_coefficient(medium[i], medium[i + 1], rule)

    A = np.zeros((nodes, nodes))
    b = np.zeros(nodes)
    for k in range(nodes):
        i = k + 1
        diag = 0.0
        for j, coef in ((i + 1, face(i)), (i - 1, face(i - 1))):
            a_f = coef
            diag += a_f
            if 1 <= j <= nodes:
                A[k, j - 1] -= a_f
            else:
                b[k] += a_f * (1.0 if j == n_intervals else 0.0)
        A[k, k] += diag
    A /= h * h
    b /= h * h
    U = np.linalg.solve(A, b)            # unknowns u_1 .. u_{n-1}
    u = np.zeros(n_intervals + 1)
    u[1:n_intervals] = U
    u[n_intervals] = 1.0
    flux = np.array([-face(i) * (u[i + 1] - u[i]) / h
                     for i in range(n_intervals)])
    return u, flux, m, h, face(m)


def chain_flux(h):
    """Closed form of Remark 2.8: resistance of the 1-D chain."""
    R = (1.0 - h) / (2.0 * AL) + h / (0.5 * (AL + AR)) + (1.0 - h) / (2.0 * AR)
    return -1.0 / R


def main():
    print(f"a_L = {AL}, a_R = {AR}, contrast c = {C:g}")
    print(f"exact flux J* = {J_STAR:.12f}")
    print(f"arithmetic face-conductance relative error "
          f"(1-c)^2/(4c) = {(1 - C) ** 2 / (4 * C):.6f}\n")

    for rule in ("harm", "arith"):
        print(f"--- {rule} ---")
        print(f"{'N':>5} {'max nodal err':>14} {'order':>7} "
              f"{'max |F-J*|':>12} {'rel':>10} {'chain F':>12} {'rel':>10}")
        previous = None
        for n in (31, 63, 127, 255):
            u, flux, m, h, a_face = solve_1d(n, rule)
            x = np.arange(1, n) * h
            err = np.max(np.abs(u[1:n] - np.array([u_exact(xx) for xx in x])))
            order = "" if previous is None else f"{np.log2(previous / err):.3f}"
            previous = err
            fmax = np.max(np.abs(flux - J_STAR))
            chain = chain_flux(h)
            print(f"{n:5d} {err:14.4e} {order:>7} {fmax:12.4e} "
                  f"{fmax / abs(J_STAR):10.3e} {chain:12.6f} "
                  f"{abs(chain / J_STAR - 1):10.3e}")
        print()

    print("Reading: 'harm' is exact to round-off at every level (nodal error and")
    print("flux error are both machine zero); 'arith' has nodal order 1 and a")
    print("flux error that halves under refinement, matching the closed-form")
    print("chain value in the last two columns.  The fixed relative error of")
    print("the interface CONDUCTANCE above is O(1) and independent of h, which")
    print("is a different quantity: it is the reason a single blanket claim of")
    print("'O(1) flux error' was replaced by the two-layer statement of the")
    print("report (Remark rem:arith_2d_boundary, Section 4.3).")


if __name__ == "__main__":
    main()
