# Project 2 — Direction 3: variable diffusion (Team Q)

Two-dimensional elliptic boundary value problem

    -div(a grad u) = f  on  (0,1)^2,      u = g  on the boundary,

with a coefficient `a` that is either smooth (`a = 1 + x`) or has a jump across
`x = 1/2` (`a = 1` for `x < 1/2`, `a = 10` for `x > 1/2`). The project compares
a conservative five-point finite-difference method with a conforming `P1`
finite-element method, and studies what happens when the interface conductance
is averaged arithmetically instead of harmonically.

## Layout

| Path | Contents |
|---|---|
| `report/` | the report sources (`Method.tex` is the master file) and the built `Method.pdf` |
| `algorithm_section/` | the reference implementation: `src/discretisation.py` (FDM and FEM assembly), `src/solvers.py` (preconditioned CG, sparse LU), `run_all.py`, tables, figures, raw results |
| `test/` | independent validation suite (`python -B -m unittest discover -s test -v`) |
| `I-PINNs/` | interface-PINN exploration, archived; not part of the report's claims |
| `meichending/` | Meichen Ding's individual package: self-contained build of the report (mathematical sections + Appendix A), the verification scripts, `Method.pdf` |
| `ics/` | Meichen Ding's ICS and AI transparency log (standalone document, format of `Checklist/ICS_bvp.tex`) |

## Reproduce

Everything below runs on CPU in double precision; BLAS threading is pinned to
one thread for reproducible timings.

```bash
cd algorithm_section
python -m pip install -r requirements.txt
python -B run_all.py            # regenerates results/ and figures/
python -B make_figures.py       # redraws figures only
```

The report is built from `report/`:

```bash
cd report
latexmk -pdf Method.tex         # TeX Live 2024 or newer; refs.bib is local
```

Independent checks that do not import the production code:

```bash
python3 report/verify/check_interface_order.py     # one-dimensional interface orders
python3 report/verify/check_stability.py           # discrete stability, barrier bound
python3 report/verify/check_matrix_evidence.py     # symmetry defect and lambda_min table
```

## Status

The numbers in the report are produced by `run_all.py`; `results/run_status.json`
records `"complete": true` when the run finished. The validation record is
`test/VALIDATION_RUN_2026-11-06.md`. The five individual contribution statements
in `report/ics/` are each authored and committed by the member they describe.
