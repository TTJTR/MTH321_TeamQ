# Verification scripts

Two self-contained scripts that reproduce the numerical checks quoted in the
**AI Transparency Log** (Appendix A) and in Appendix A, Audit 1 and 2. They
depend only on NumPy and run in a few seconds; they do not import the project
solver, which is the point --- they are independent of the implementation they
are used to check.

```bash
python3 verify/check_interface_order.py     # Appendix A, Audit 1 (one dimension)
python3 verify/check_stability.py           # Appendix A, Audit 2 (discrete stability)
```

## `check_interface_order.py`

Solves the one-dimensional layered benchmark with a vertex-centred conservative
scheme for `N = 31, 63, 127, 255` (odd, so the interface lies between two
columns) using both the harmonic and the arithmetic interface conductance, and
reports

* the maximum nodal error against the exact solution,
* the measured order between consecutive meshes,
* the maximum face-flux error against the exact `J* = -20/11`,
* the closed-form chain flux of Remark 2.8 (`rem:arith_2d_boundary`).

Expected reading: harmonic is exact to round-off in both fields; arithmetic has
nodal order 1 and a flux error that halves under refinement, matching the
closed form. The interface **conductance** relative error is `2.025` at every
level, independent of `h` --- that is the `O(1)` quantity, and it is not the
same as the flux error of the solved solution. This is the distinction that
Appendix A, Audit 1 records.

## `check_stability.py`

Checks the two claims of Theorem 2.10 and the counterexample of
Remark 2.13 (`rem:entrywise_false`):

* `max |A_h phi - 1|` with `phi = x(1-x)/2` (one dimension) and the analogous
  function in two dimensions --- the discrete Laplacian applied to a quadratic
  is exact, so this is round-off;
* `max w` against the barrier bound `1/(8 a_min)`, and `w <= phi`;
* the failure of the entrywise inequality that a Loewner-order argument does
  not imply: for `a = 1 + 9 sin^2(pi x)`, `n = 63`, the ratio of the two
  entries of `A^{-1}` reaches about `3.10`.

These are the numbers quoted in Theorem 2.10, Remark 2.13 and Appendix A,
Audit 2; unit tests are in `test/`.
