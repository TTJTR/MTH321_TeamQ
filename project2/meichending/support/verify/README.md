# Verification scripts (Meichen Ding)

Three self-contained scripts that reproduce every numerical claim I quote in the
report appendix and in §2.4. The first two depend only on NumPy and do **not**
import the project solver — that independence is the point, they are used to
check the implementation rather than to agree with it. The third imports the
team's assembler on purpose, because its job is to corroborate the matrix that
is actually submitted.

```bash
python3 project2/meichending/support/verify/check_interface_order.py
python3 project2/meichending/support/verify/check_stability.py
python3 project2/meichending/support/verify/check_matrix_evidence.py
```

Expected run time: a few seconds each.

## `check_interface_order.py` — audit 1

Solves the one-dimensional layered benchmark with a vertex-centred conservative
scheme on `N = 31, 63, 127, 255` (odd, so the interface lies between two columns)
using both the harmonic and the arithmetic interface conductance, and reports

* the maximum nodal error against the exact solution and the measured order,
* the maximum face-flux error against `J* = -20/11`,
* the closed-form chain flux of the remark on the two-dimensional boundary
  (`rem:arith_2d_boundary`).

Measured output: harmonic exact to round-off in both fields; arithmetic nodal
error `1.9417e-2 → 9.6085e-3 → 4.7793e-3 → 2.3834e-3` with orders
`1.015 / 1.008 / 1.004`, flux relative error `2.207e-2 → 2.632e-3`, identical to
the closed-form chain value to every printed digit. The interface **conductance**
relative error is `2.025` at every level, independent of `h`: that is the `O(1)`
quantity, and it is not the flux error of the solved problem. Distinguishing the
two is what audit 1 records.

## `check_stability.py` — audit 2

Checks the stability claims of §2.4 and the counterexample of
`rem:entrywise_false`:

* `max |A_h phi - 1|` with `phi = x(1-x)/2` in one dimension and the analogous
  function in two — the discrete Laplacian applied to a quadratic is exact, so
  this is round-off;
* `max w` against the barrier bound `1/(8 a_min)`, and `w <= phi`;
* the failure of the entrywise inequality that a Loewner-order argument does not
  imply: for `a = 1 + 9 sin^2(pi x)`, `n = 63`, the ratio of the two entries of
  `A^{-1}` reaches `3.1024 > 1`.

Measured output: entrywise inequality `FAILS` at `3.1024`; `||A^{-1}||_inf` is
`0.0861` (1D, `n = 63`) and `0.0502` (2D, `n = 14`) against the bound `0.125`, so
the bound itself survives while the proof route does not. That is why the report
proves it with a maximum-principle barrier instead.

## `check_matrix_evidence.py` — §2.4, table 5

Produces the table required by Direction 3 of the problem pack: the symmetry
defect `||A - A^T||/||A||`, an `eigsh` smallest-eigenvalue estimate and a dense
Cholesky factorisation, all on the submitted assembler
(`project2/algorithm_section/src/discretisation.py`) for the smooth and layered
cases.

Measured output: defect exactly `0` in the max and Frobenius norms for every
case; `λ_min = 28.675, 28.694, 44.250, 44.346, 48.848` against the bound
`8 a_min = 8`; Cholesky succeeds everywhere. The defect is zero by construction
(each off-diagonal entry is written twice from the same shared face
coefficient), so these numbers corroborate the derivation rather than replace
it.
