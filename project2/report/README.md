# Project 2 report — Team Q

## Read the report

[**MTH321_Project2_TeamQ_Report.pdf**](MTH321_Project2_TeamQ_Report.pdf)

This is the current 50-page report. `Method.pdf` is the identical compatibility
build copy; `Method.tex` remains the LaTeX entry. Download the complete
`report/` directory to compile it, including section files, references,
figures, tables and `APPENDIX/`. Report content was not changed by the filename
and README update.

## Structure

| Part | Source |
|---|---|
| Introduction, model and discrete analysis | [Method.tex](Method.tex) |
| Algorithm and implementation | [algorithm_section.tex](algorithm_section.tex) |
| Verification, experiments and limitations | [results_section.tex](results_section.tex) |
| Interface PINN and single-network ablation | [interface_pinn_section.tex](interface_pinn_section.tex) |
| Conclusions | [conclusion.tex](conclusion.tex) |
| Bibliography | [refs.bib](refs.bib) |
| Appendix A: contributor AI records | [APPENDIX/](APPENDIX/) |
| Appendix B: five individual contribution statements | `APPENDIX/ICS_*_body.tex` |
| Appendix C: reproducibility/provenance | End of `Method.tex` |
| Appendix D: assessment evidence index | [EVIDENCE_INDEX.tex](APPENDIX/EVIDENCE_INDEX.tex) |

The PDF includes submitted statements without adding signatures. Jingyan's
source retains its contributor-supplied DRAFT comment. Confirmation and
signing remain the members' responsibility.

## Rebuild figures and PDF

From `project2/`, in the established course environment:

```text
python -B code/run_all.py --build-report
```

This regenerates all nine external figures and the native TikZ architecture,
then publishes both the formally named PDF and `Method.pdf`. pdfLaTeX and
BibTeX must be on PATH. See [environment notes](../ENVIRONMENT.md) and
[project commands](../README.md). No neural training is performed.

For a document-only edit, compile from this `report/` directory using an
existing build directory and repeat only as needed to resolve references:

```text
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Method.tex
bibtex build/Method
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Method.tex
pdflatex -interaction=nonstopmode -halt-on-error -output-directory=build Method.tex
```

Create `build/` first. The intermediate result is `build/Method.pdf`; publish
it as `MTH321_Project2_TeamQ_Report.pdf` and update `Method.pdf` together.
BibTeX is only needed when rebuilding the bibliography. Inspect affected
pages and references after an edit; the complete numerical suite need not be
rerun for a caption or documentation change.

## Evidence and figures

- [support/interface_pinn/](support/interface_pinn/): all six checkpoints,
  configuration, model code, training logs, source hashes and `comparison.json`.
  The replay uses three seeds per architecture and the same evaluation points.
- [support/verify/](support/verify/): independent interface/stability models
  and the matrix check importing the production assembler.
- [support/ai_log/](support/ai_log/): contributor-supplied audit extracts.
- [figures/](figures/): vector PDFs for LaTeX and 300-dpi PNG previews. File
  stems such as `fig07_mesh` are asset names, not report figure numbers.
- [tables/](tables/): reported measurement snapshots. Preserve their original
  timing provenance when rerunning numerical experiments on other hardware.

Run individual replay or plotting scripts from the commands in the
[project README](../README.md). Source paths in Appendix D are relative to
`project2/`; paths in Section 5.4 are relative to this report directory, as
stated there. The canonical current checks are in the
[checklist](../reviews/CHECKLIST_STATUS.md) and its linked evidence.
