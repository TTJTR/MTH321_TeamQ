# Project 2 integrated report — local review

This local version combines main at `cc39c69` and
`meichen/appendices-ics` at `248cc8d`. It has not been pushed to GitHub.

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
- Individual statements: the four `ICS_*_body.tex` files under `APPENDIX/`,
  extracted from submitted statements and formatted one per page.
- Original contributor files remain available. The integrated writing log
  omits three empty audit slots and corrects stale Project 1 terminology.
  The Han Liu body escapes the ampersand in the role description for LaTeX.
- No signature is generated. Jingyan Wei's statement is still outstanding.
- The new Interface PINN comparison and training plots are supplementary
  material and are not added to the report body by this merge.

The preview is therefore a merged review copy, not a claim that all final
submission items are complete. No numerical experiment was rerun.
