# Theory verification scripts (Meichen Ding)

Three small, self-contained checks behind the theory side of the report. Each
prints its own reading instructions; none of them needs the report to build.

Run from `project2/` (the parent of `algorithm_section/`), Python 3 with NumPy
and SciPy only:

```bash
cd project2
python3 meichending/support/verify/check_matrix_evidence.py   # Table 1
python3 meichending/support/verify/check_interface_order.py   # Sec. 4.3, one dimension
python3 meichending/support/verify/check_stability.py         # Remark on the entrywise claim
```

| Script | Reproduces | Independent of |
|---|---|---|
| `check_matrix_evidence.py` | symmetry defect 0, `lambda_min` = 28.675 / 28.694 / 44.250 / 44.346 / 48.848 against `8 a_min = 8`, dense Cholesky | imports the **submitted** assembler on purpose, so the numbers are not a re-implementation |
| `check_interface_order.py` | harmonic exact to round-off, arithmetic nodal order 1.015 / 1.008 / 1.004, flux relative error 2.207e-2 -> 2.632e-3, closed-form chain value | own one-dimensional tridiagonal solve |
| `check_stability.py` | entrywise ratio 3.1024 > 1 (the claim is false), `||A^-1||_inf` = 0.0861 (1D) and 0.0502 (2D) against 0.125 | own assembly; the bound is checked, not assumed |

Known limitations: the 0.662 interface-flux maximum is a boundary effect of the
prescribed horizontal Dirichlet data and is reported as an observation on this
benchmark; `1/(8 a_min)` is an upper bound in two dimensions (the observed
maximum is 0.0736), and equality holds only in one dimension.
