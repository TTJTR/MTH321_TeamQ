# Code review — Project 2 (Direction 3)

Reviewer: Meichen Ding (2362344). Date: 2026-11-15.
Form: `Checklist/code_review_checklist_bvp.tex`, sections A–H.
Scope reviewed: `algorithm_section/` (production FDM and P1-FEM code),
`test/` (independent validation), `report/` (numbers quoted from the code).
Environment: Python 3, NumPy/SciPy/Matplotlib, single-threaded BLAS, no GPU.

Everything below was **run**, not read: `python -B run_all.py` exits 0 and
regenerates six figures and four LaTeX tables, `python -B -m unittest discover
-s test -v` passes, and the three theory checks in `report/support/verify/`
reproduce the numbers quoted in Appendix A.

---

## A. Does it run?

- [x] `python -B run_all.py` runs from `algorithm_section/` with no manual edits
      (exit 0; six figures, four tables, all CSVs rewritten).
- [x] Requirements are stated (`project2/README.md`, `algorithm_section/requirements.txt`):
      NumPy, SciPy, Matplotlib. No `scikit-fem`, no `pyamg`, no GPU.
- [x] Entry point documented; a second script (`make_figures.py`) redraws figures
      from saved data without re-solving, and `run_all.py:159` calls it.

## B. Is the model what the report says?

- [x] Operator matches §2.1: `assemble_fdm` (`src/discretisation.py:43`) builds the
      five-point stencil from **one shared face conductance per edge**, not from two
      one-sided differences; `average=` switches arithmetic vs harmonic.
- [x] Coefficients are centralised (`coefficient`, `src/discretisation.py:27`), and
      the contrast is a parameter, not a literal scattered through the code.
- [x] Boundary conditions: Dirichlet on all four sides; the RHS carries the
      contribution of the eliminated boundary values with the correct sign
      (checked against the hand-computed 4×4 matrix below).
- [x] The FEM side assembles the same weak form (`assemble_fem`,
      `src/discretisation.py:124`) with an interface-aligned mesh, so the
      comparison is of discretisations, not of two different problems.

## C. Is the discretisation right?

- [x] Interior rows follow the stencil exactly; the index map `k=(i-1)n+(j-1)` and
      the two-dimensional neighbour offsets are implemented once and reused
      (`src/discretisation.py`), and the boundary rows agree with the index map
      at the two ends and in the centre.
- [x] Matrix is genuinely sparse (COO→CSR, `nnz = 5n^2-4n = 19593, 80137`), and a
      spy plot matches the predicted pattern (`fig02_sparse_assembly`).
- [x] Small-case oracle: the `n=2` hand-computed 4×4 matrix is reproduced by the
      assembler element by element (`test/test_validation.py`).
- [x] Dirichlet right-hand side checked by an affine patch with asymmetric values
      on all four sides: agreement with an independently assembled dense
      reference to 4.89e-15.

## D. Is the solver honest?

- [x] Stopping criterion is the **explicit residual**, not the step difference
      (`src/solvers.py:27`, `residuals` at `src/solvers.py:7`).
- [x] Tolerance sweep at fixed mesh (`Tables 2`): at rtol 1e-12 the CG solution
      agrees with sparse LU to 5.33e-15 (FDM) and 1.01e-14 (FEM), i.e. the
      algebraic error is far below the discretisation error (~8e-4).
- [x] Iteration counts are reported with the tolerance that produced them.
- [x] Direct and iterative paths are independent (SuperLU factorisation vs CG).

## E. Are the numbers trustworthy?

- [x] Four named norms per mesh (`E_{2,h}`, `E_inf`, common P1-integrated L²),
      fitted orders 2.00 for both methods; layered orders 0.991/0.995/0.998.
- [x] Claims match the measurements: no "stable/converged/accurate" without a
      number; the layered maximum flux error is reported as non-decreasing, which
      is what the data show.
- [x] Hard problems are only used after an easy check: the smooth manufactured
      benchmark and the analytic bank come before the layered and PINN results.
- [x] The 0.662 interface-flux maximum is flagged as a boundary effect of the
      prescribed horizontal data rather than as a general error estimate.

## F. Can it be maintained?

- [x] Assembly, solve and verification are separated (`src/discretisation.py`,
      `src/solvers.py`, `test/`).
- [x] Mesh sizes, contrasts, tolerances and quadrature order live in
      `algorithm_section/config.json`, not inline.
- [x] No absolute paths (checked `grep -rn "/Users/\|C:\\\\"` → 0 hits), no dead code found.

## G. Findings

| # | Severity | Location | What is wrong | Fix |
|---|---|---|---|---|
| 1 | major | `project2/README.md` | Was 0 bytes: the one-command reproduction path existed only in a Chinese README inside `algorithm_section/` | Written in this commit (English, layout, requirements, commands, figure/table provenance) |
| 2 | major | `report/` | The submitted PDF could not be rebuilt from the repository: `report/Method.tex` was the old 796-line version and the §5 PINN source was absent | Report source committed in this commit (`report/` replaced by the version that builds the 44-page PDF) |
| 3 | minor | `I-PINNs/*.log`, `algorithm_section/results/tests.log`, `test/results/*.log` | Run logs are tracked, so every run dirties the working tree | `.gitignore` added; the tracked copies should be removed in a follow-up commit by the owner of those files |
| 4 | minor | `algorithm_section/figures/*.png` | Each figure is committed twice (PDF for LaTeX, PNG for reading); the PNGs are never used by the build | Keep, but note it; or generate PNGs on demand |
| 5 | minor | `test/` | Three tests are skipped unless `MTH321_TEST_BANK` points at the course bank, so a plain `unittest` run looks greener than it is | Documented in `project2/README.md`; the run with the bank is recorded as 9 passed / 32 solves |
| 6 | minor | `algorithm_section/results/cost.csv` | Wall-clock timings depend on machine and BLAS threading; re-running the suite on another laptop changes them | Stated in the report (median of three local repetitions) and in the README |
| 7 | info | `algorithm_section/tests/` vs `project2/test/` | Two directories with "test" in the name hold different things (solver micro-tests vs the validation suite) | Leave as is; README explains which is which |

## H. Three things to fix before submission

1. **Commit the report source** so `latexmk -pdf Method.tex` rebuilds the submitted
   PDF from a clean clone (done in this commit; verify after merge).
2. **Keep the top-level README current** — it is the first file a marker opens.
3. **Stop tracking logs and build products** (`.gitignore` added; the already
   tracked files need one follow-up commit from their owners).

Positive: the validation suite is not a mirror of the production code — the
manufactured forcing is differentiated independently, the boundary elimination is
compared against a dense reference, and the small-case matrix is hand-computed.
The tolerance sweep is a genuinely separate mechanism from the convergence study,
and the report says so.
