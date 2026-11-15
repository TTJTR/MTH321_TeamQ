# Project 2 report — LaTeX source

Master file: `Method.tex` (44 pages). Build:

```bash
latexmk -pdf Method.tex          # -> Method.pdf
latexmk -C                       # clean
```

Everything is included from the same directory; no absolute paths, no shell
escape, no external data files are needed at build time.

## Files

| File | Contents |
|---|---|
| `Method.tex` | preamble, §1–§2, and the `\input` list for §3–§6 and the appendices |
| `algorithm_section.tex` | §3 Implementation (data layout, solvers, cost, diagnostics) |
| `results_section.tex` | §4 Verification and numerical experiments (incl. §4.5 Limitations) |
| `interface_pinn_section.tex` | §5 Interface PINN baseline |
| `conclusion.tex` | §6 Conclusions |
| `tables/*.tex` | generated tables (copy of the CSV values) |
| `figures/fig0*.pdf` | Figures 1–6, 8–9 (Figure 7 does not exist; numbering skips it deliberately) |
| `APPENDIX/` | AI transparency log (three contributor files) and the five individual contribution statements |
| `support/verify/` | the three theory checks cited in Appendix A and §4.3 (NumPy/SciPy only) |
| `support/interface_pinn/` | archived PINN checkpoints, replay script, figure script |
| `src/discretisation.py` | copy of the production assembler, so the matrix evidence can be re-run from this folder |

## Which numbers come from where

| Report object | Produced by |
|---|---|
| Tables 1–7 | `../algorithm_section/run_all.py` → `results/*.csv` |
| Matrix-evidence table | `support/verify/check_matrix_evidence.py` (imports `src/discretisation.py`) |
| §4.3 one-dimensional flux chain and orders | `support/verify/check_interface_order.py` |
| Remark on the entrywise claim (ratio 3.10) | `support/verify/check_stability.py` |
| Figures 1–6 | `../algorithm_section/make_figures.py` |
| Figures 8–9 | `support/interface_pinn/make_figures.py` |
| Appendix tables A.1–A.4 | hand-written records, no code dependency |

## Verification scripts

```bash
python3 support/verify/check_matrix_evidence.py   # symmetry defect 0, lambda_min >= 8 a_min, Cholesky ok
python3 support/verify/check_interface_order.py   # harmonic exact to round-off, arithmetic first order
python3 support/verify/check_stability.py         # entrywise ratio 3.1024 > 1, ||A^-1||_inf vs 1/(8 a_min)
```

## Build status

Compiled 2026-11-15 with pdfTeX (TeX Live 2026): 44 pages, 0 errors,
0 overfull/underfull boxes, 0 undefined references, 0 undefined citations,
0 LaTeX warnings.
