# Project 2 integrated report

This local version combines main at `cc39c69` and
`meichen/appendices-ics` at `248cc8d`. The integration preserves both submitted branches.

## Build

Run from this directory with a working pdfLaTeX/BibTeX installation:

```text
mkdir build
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Method.tex
bibtex build/Method
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Method.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Method.tex
```

The entry point is `Method.tex`. The existing algorithm, results, figures
and data tables are retained from main. Theory additions and the matrix
evidence table come from Meichen Ding's submitted package.

## Appendices

- AI records: `AI_Theory_MeichenDing.tex`, `TianruiJi_AI_Transparency.tex`
  and `AI_Writing_HanLiu.tex` under `APPENDIX/`.
- Individual statements: the five `ICS_*_body.tex` files under `APPENDIX/`,
  extracted from submitted statements and formatted one per page.
- Original contributor files remain available. The integrated writing log
  omits three empty audit slots and corrects stale Project 1 terminology.
  The Han Liu body escapes the ampersand in the role description for LaTeX.
- Jingyan Wei's supplied statement is included; all five ICS source files
  are now present. The supplied Jingyan source is marked DRAFT in comments;
  integration does not confirm attribution or supply signatures.
- Section 5 includes the Interface PINN architecture, training records and
  common-point FDM/FEM comparison. Evidence and replay commands are under
  `support/interface_pinn/`.

The preview is therefore a merged review copy, not a claim that all final
submission items are complete. The new section replays three archived
checkpoints and solves classical reference systems; no neural training was rerun.


## Interface PINN replay and visualisation fixes

Run from `project2/report`:

```text
python -B support/interface_pinn/reevaluate.py
python -B support/interface_pinn/make_figures.py
```

The replay ran successfully in the local `dl` environment (PyTorch 2.7.1 CPU).
It evaluated all three archived c=10 checkpoints and solved the classical
references: mean sampled relative PINN error 3.1171e-5, mean maximum absolute
flux error 1.3677e-3; FDM and fitted FEM errors below 1e-12 on this benchmark.
Configuration, all three checkpoints, matching model source, raw logs,
comparison.json and plotting code are included under `support/interface_pinn/`.
This replay uses a different protocol from `project2/test/recheck_pinn.py`;
the two scripts must not be substituted without changing the reported norms.

To regenerate only the revised classical visualisations from saved data:

```text
cd ../algorithm_section
python -B make_figures.py --review
```

Copy the generated fig03, fig04, fig05 and fig07 PDF/PNG files into the
report's `figures/` directory before building the report. No training or
full numerical experiment is required. Blue is FDM, orange is FEM, purple
is Interface PINN; green/magenta distinguish harmonic/arithmetic faces.
Training seeds and coefficient contrasts use grey shades. The signed-error
colour scale is symmetric about zero. The cost panel states Jacobi-CG
rtol=1e-12, atol=0. Figure 07 shows the actual grid and triangular mesh.


## Unified entry and November 15 branch integration

From `project2`, run `python -B code/run_all.py` to regenerate every external
report figure and sync it here. `--build-report` also rebuilds the native
TikZ architecture and PDF. The new Meichen source/review branch supplies
canonical theory checks under `support/verify/`, a corrected flux value,
limitations and contributor AI evidence. The current vector plots and mesh
illustration are retained. The common-point replay now includes three
single-network checkpoints as a secondary, non-parameter-matched ablation.
See `../reviews/CHECKLIST_STATUS.md` for checks and remaining manual items.


## Evidence index integration (2026-11-16)

Appendix D integrates Meichen's evidence index from commit 9dffbd3.
Paths start at `project2/`, figure/table references use automatic labels,
and cost/midline-flux sources and finest-three fitted orders match the archive.
It distinguishes the independent small-model checks from the matrix script
that imports production code, and points to the unified entry, six-checkpoint
replay and bank-enabled passing validation. Only the new appendix and related
references were checked; no experiment or training was rerun.


The course base environment is fixed and reused from the team's established
setup. See `../ENVIRONMENT.md` for Project 1 context and the separate PyTorch
extension. The Figure 5 caption now distinguishes fitted grey lines from
the separately labelled h-squared reference; the plot and data are unchanged.
