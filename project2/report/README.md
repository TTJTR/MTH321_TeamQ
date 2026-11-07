# Report sources

`Method.tex` is the master file; it `\input`s the section files and the
appendices.

| File | Contents |
|---|---|
| `Method.tex` | preamble, title page, Sections 1–2, table of contents, appendix wiring |
| `algorithm_section.tex` | Section 3: implementation, solvers, measured cost |
| `results_section.tex` | Section 4: verification and numerical experiments |
| `conclusion.tex` | Section 5: conclusions and limitations |
| `appendix_ai_log.tex` | Appendix A: AI transparency log (tools, claim audits, verification, ownership) |
| `ics/` | Appendix B: one individual contribution statement per member |
| `tables/` | table fragments used by Section 4 |
| `figures/` | figure PDFs used by Section 3 |
| `verify/` | independent NumPy scripts quoted in Appendix A and Appendix C |
| `refs.bib` | bibliography |

## Build

```bash
latexmk -pdf Method.tex      # TeX Live 2024 or newer
latexmk -C                   # remove build products
```

The build needs `refs.bib` in this directory, `figures/` and `tables/` as
shipped, and nothing else. A clean clone builds with zero errors, zero overfull
boxes and zero undefined references; the result is the committed `Method.pdf`.

Intermediate files (`*.aux`, `*.log`, `*.toc`, ...) are ignored by
`report/.gitignore`.
