# Current integrated report (v3)

The 42-page report comprises an abstract, Sections 1–4 on the model, theory, implementation and baseline experiments, Section 5 on two-stage Gauss implicit RK4, Section 6 with conclusions, references, and Appendices A–C. Build `report.tex` from this directory with `pdflatex -interaction=nonstopmode -halt-on-error report.tex`, repeating until cross-reference warnings disappear (three passes from a clean directory).

| File or directory | Purpose |
|---|---|
| `report.tex`, `report.pdf` | LaTeX entry point and compiled report. |
| `sections/section1.tex` | Background and problem. |
| `sections/section2.tex` | Baseline theory, stability and Newton pseudocode. |
| `sections/section3.tex` | Implementation, adaptive controller and pseudocode. |
| `sections/section4.tex` | Baseline numerical evidence and validation. |
| `sections/section5.tex` | Advanced Gauss IRK4 method and comparison. |
| `sections/section6.tex` | Conclusions. |
| `appendices/appendix_a.tex` | AI transparency log. |
| `appendices/appendix_b.tex` | Individual contribution statements. |
| `appendices/appendix_c.tex` | Baseline data dictionary and figure mapping. |
| `references.tex` | References. |
| `figures/` | Eight baseline and four advanced comparison PNGs. |
| `data/` | Six baseline CSVs and `summary.json`. Advanced CSVs/JSON are in project-level `data/advanced_irk4/`. |
| `checklist/` | Current acceptance checklist and historical validation record. |
| `manifest.json` | SHA-256 inventory for submitted files. |

## Figures

| Figure | Interpretation |
|---|---|
| `convergence.png` | Full-matrix terminal error versus step size and observed orders. |
| `cost_accuracy.png` | RHS work versus achieved error, including matched-accuracy points. |
| `stability_regions.png` | Scalar stability regions and initial Jacobian modes. |
| `frozen_spectrum.png` | Initial Jacobian spectrum and local explicit-step cutoffs. |
| `stability_sweep.png` | Nonlinear perturbation amplification and finite-time error. |
| `trajectory_diagnostics.png` | Singular values, energy, orthogonality defect and Lyapunov residual. |
| `adaptive_steps.png` | Accepted step lengths and estimated local error. |
| `rank_deficient.png` | Persistence of the zero singular value and partial-isometry limit. |
| `advanced_irk4/convergence_comparison.png` | Gauss IRK4 and baseline convergence. |
| `advanced_irk4/cost_comparison.png` | Error versus computational work for the advanced comparison. |
| `advanced_irk4/energy_comparison.png` | Energy behavior across methods. |
| `advanced_irk4/stability_comparison.png` | Stability comparison for the additional method. |

The [project README](../README_EN.md) explains the baseline code and data fields. The [advanced README](../code_advanced/README.md) explains the additional solver and comparison.
