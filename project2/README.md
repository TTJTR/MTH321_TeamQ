# Project 2 — Interface Bundles for Elliptic BVPs (Direction 3, Team Q)

Elliptic boundary value problem with a discontinuous diffusion coefficient on the
unit square, solved with a **conservative finite-difference scheme** on shared
face conductances and compared with a matched **conforming P1 finite-element**
implementation, plus an archived interface-PINN baseline.

## Layout

| Path | Contents |
|---|---|
| `report/` | LaTeX source of the submitted report (`Method.tex` is the master) |
| `algorithm_section/` | production FDM/FEM code, `run_all.py`, results and figures |
| `test/` | independent validation suite, including an optional run against the course bank |
| `support/interface_pinn/` | archived PINN checkpoints, replay script, figure script |
| `reviews/` | code-review record (Project 2) |

## Requirements

Python 3 with NumPy, SciPy and Matplotlib (`pip install numpy scipy matplotlib`).
The report needs a LaTeX installation with `booktabs`, `longtable`, `mdframed`,
`algpseudocode` and `subcaption` (TeX Live or MiKTeX, `latexmk` recommended).
No GPU and no neural-network framework is needed to reproduce the reported
numbers: the PINN results are replayed from archived checkpoints.

## Reproduce everything

```bash
cd algorithm_section
python -B run_all.py        # assembles, solves, writes results/*.csv and the tables
python -B make_figures.py   # redraws figures/ from results/ only (no solving)
```

`run_all.py` prints one line per experiment and exits non-zero on failure.
Numbers go to `results/*.csv` (and `.npz` for the solution fields), the tables of
the report are generated from those files.

Validation:

```bash
python -B -m unittest discover -s test -v        # 8 passed, 3 skipped by default
MTH321_TEST_BANK=/path/to/test_problem_bank.py python -B -m unittest discover -s test -v
```

With the course bank enabled the suite runs 32 solver solves and 9 tests pass.
`MTH321_STRICT_VALIDATION=1` turns the known-defect tests into expected failures;
that mode is expected to exit non-zero on the pinned snapshot.

Report:

```bash
cd report
latexmk -pdf Method.tex     # -> Method.pdf, 44 pages
```

## Where each figure and table comes from

| Artefact | Produced by |
|---|---|
| Figures 1–6 (`figures/fig01…fig06`) | `algorithm_section/make_figures.py` |
| Figures 8–9 (PINN training and accuracy) | `support/interface_pinn/make_figures.py` |
| Tables 1–7 of the report | `algorithm_section/run_all.py`, written to `results/*.csv`, then copied into `tables/` |
| Matrix-evidence table | `support/verify/check_matrix_evidence.py` |
| Appendix tables A.1–A.4 | no code dependency (hand-written records) |

## Known gaps

- `algorithm_section/make_figures.py` regenerates every figure from saved data;
  the two PINN figures need the archived checkpoints in
  `support/interface_pinn/archive/`, not a GPU.
- Timings in the cost table are local CPU measurements from one machine; they are
  ratios, not absolutes, and will move with hardware and BLAS threading.
- The layered benchmark has an exact solution in `H^1` but not in `H^2`; the
  layered results are exactness and defect statements, not convergence orders.
