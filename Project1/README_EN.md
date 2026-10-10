# MTH321 Project 1: Polar-Factor Gradient Flow

## Run the project

Use Python 3.10 or newer. In the `Project1` directory:
The recorded results were produced with Python 3.12.4, NumPy 1.26.4,
SciPy 1.13.1 and Matplotlib 3.8.4.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -B code/run_all.py
.venv\Scripts\python -B -m unittest discover -s test -v
```


The entry point writes all twelve report PNGs: eight baseline figures to
project-level `figures/` and four advanced comparison figures to
`figures/advanced_irk4/`. It also writes six baseline CSVs plus
`summary.json` to `data/`, and two advanced CSVs plus `summary.json` to
`data/advanced_irk4/`. It does not overwrite archived reports.
The JSON records actual software versions.

## Model and verification

The assignment's Topic 5 benchmark is

```text
X'(t) = X(t) [I - X(t)^T X(t)]
X(0)  = R(0.4) diag(0.2, 1.4, 3) R(-0.7)^T .
```

The solver state is `vec(X)` in **column-major** order (`order='F'`). We
implement Explicit Euler, classical RK4, and Implicit Euler with damped
Newton iteration. The exact finite-time matrix is reconstructed from the
initial SVD,
`X_exact(t)=U diag(s_i(t)) V^T`, with
`s_i(t)=s_i(0)/sqrt(s_i(0)^2+[1-s_i(0)^2]exp(-2t))`.
It is used to **measure** numerical error, never to advance a numerical step.
SciPy `solve_ivp(method='Radau')` is a separate reference check; it is not
one of the three methods being compared.

## What each source file does

| File | Purpose |
|---|---|
| `code/model.py` | Constructs the prescribed and rank-deficient initial matrices; converts matrices to/from column-major states; evaluates the matrix RHS, Fréchet derivative and analytic Jacobian; computes the finite-time SVD solution, singular values, Lyapunov energy/rate and orthogonality defect. |
| `code/solvers.py` | Implements the three one-step methods, the damped Newton solve for Implicit Euler, uniform-grid integration and step-doubling adaptivity. Counts RHS evaluations, Jacobian evaluations, Newton iterations and rejected trials. |
| `code/experiments.py` | Runs all numerical studies, plots eight figures, exports six CSV files and writes the machine-readable summary. |
| `code/run_all.py` | Single command-line entry point; runs the baseline experiments and the separate advanced comparison, then prints the fitted baseline orders and reference disagreement. |
| `test/test_validation.py` | Checks the analytic Jacobian against finite differences, both full spectra, the energy identity, the diagonal scalar sanity case, the SVD/Radau comparison, convergence orders, adaptive behavior, the rank-deficient case, tolerance sensitivity, large-step singular-value crossing and Newton retry. |
| `report_v3/checklist/README.md` | Acceptance checklist, evidence, figure mapping and reproduction commands. |
| `report_v3/checklist/VALIDATION_RUN_2026-10-03.md` | Historical bilingual reproduction record, retained for provenance. |
| `report_v3/sections/section1.tex` | Background and motivation for the polar-factor gradient flow. |
| `report_v3/sections/section2.tex` | Theory and Newton pseudocode (Algorithm 1). |
| `report_v3/sections/section3.tex` | Implementation and adaptive pseudocode (Algorithm 2). |
| `report_v3/sections/section4.tex` | Experiments, results and verification coverage. |
| `report_v3/sections/section5.tex` | Advanced two-stage Gauss implicit Runge--Kutta method and comparison. |
| `report_v3/sections/section6.tex` | Conclusions and synthesis of the main numerical findings. |
| `report_v3/appendices/appendix_a.tex` | AI Transparency Log. |
| `report_v3/appendices/appendix_b.tex` | Individual Contribution Statements. |
| `report_v3/appendices/appendix_c.tex` | Data/figure map, field dictionary and numerical extracts. |
| `requirements.txt` | Lists NumPy, SciPy and Matplotlib. |
| `CODE_HANDOFF.md` | Numbers and interpretation for integrating the code results into report Sections 3–4. |
| `report_v3/report.tex` | Complete report containing the abstract, Sections 1--6, references and Appendices A--C. |
| `slides/Topic5_presentation.tex` | Source for the 11-slide presentation draft; `slides/Topic5_presentation.pdf` is the compiled deck. |
|`report_v3/CHANGELOG.md` | Records v3 integration, updates and verification. |
## What each figure shows


The current report bundles eight baseline PNGs and four advanced-method PNGs in `report_v3/figures/`, and six baseline
CSVs plus JSON in `report_v3/data/`, so compilation does not require
running Python first. Appendix C provides their mapping, field definitions
and numerical extracts. `report_v1/` and `report_v2/` remain preserved as
historical snapshots.
`report_v1/` remains unchanged.

| Figure | Meaning and companion data |
|---|---|
| `convergence.png` | Three log-log panels show terminal **full-matrix Frobenius error** against fixed step size, theoretical `h¹`/`h⁴` slopes, fitted lines and 95% regression bands. `convergence.csv` contains `N`, `h`, error, adjacent observed order and work counts. RK4's fit uses its finest three grids. The band is a descriptive least-squares diagnostic for deterministic data, not a probability statement about the ODE error. |
| `cost_accuracy.png` | Log-log **achieved error versus RHS evaluations** across several fixed grids for each method. Stars identify the three matched-error points near `9×10⁻⁴`; the grey band spans their actual errors. `cost_accuracy.csv` has all plotted points, `matched_point`, step counts, RHS/Jacobian evaluations and Newton iterations. See the cost caveat below. |
| `stability_regions.png` | Three analytic scalar-test regions `|R(hλ)|≤1`, with the initial Jacobian modes overlaid at `h=0.08`: crosses contract, while the open circle is a physical growth mode. Shading comes from stability functions, not a nonlinear simulation. There is no companion CSV. |
| `frozen_spectrum.png` | Initial 9×9 Jacobian eigenvalues scaled by `h=0.05` and `h=0.10`, with negative-real Euler and RK4 cutoffs. The two labelled rows identify step sizes; vertical positions are not imaginary parts. The positive eigenvalue `+0.88` is physical growth of the initially small singular value. The numbers are in `summary.json`. |
| `stability_sweep.png` | One-step amplification of a small perturbation in the fastest initial direction, and terminal exact-matrix error over several fixed step sizes. `stability_sweep.csv` additionally gives energy changes, singular-value crossing and failed-run status. Frozen-Jacobian cutoffs are local diagnostics, not global nonlinear stability guarantees. |
| `trajectory_diagnostics.png` | Four panels: singular values versus their labelled exact curves, numerical and exact Lyapunov energy, numerical and exact finite-time orthogonality defect, and the discrete Lyapunov identity residual. `trajectory.csv` records the plotted trajectory and the residual associated with the following interval. |
| `adaptive_steps.png` | Accepted step sizes for the three step-doubling solvers. `adaptive_steps.csv` gives each accepted start time, step length and normalized **estimated local** error. A short final step may simply land exactly on `t=2`. |
| `rank_deficient.png` | Numerical singular values and dashed exact curves when the first initial singular value is zero. `rank_deficient.csv` records both paths over `[0,8]`; the zero mode stays at floating-point scale and the limit is a partial isometry. |

`summary.json` contains the interval, software versions, all numerical settings,
convergence slopes, initial and equilibrium spectra, local stability estimates,
matched-accuracy work counts, adaptive statistics and rank-deficient
diagnostics. CSV `status=diverged_or_failed` means that a large-step run did
not complete; blank or `nan` measurements in that row are not zero errors.

## Reproducible settings and interpretation

| Study | Settings |
|---|---|
| Main benchmark | `t∈[0,2]`; initial singular values `(0.2,1.4,3)`. |
| Fixed-step order | Euler and Implicit Euler: `N=40,80,160,320`; RK4: `N=40,80,160,320,640,1280,2560`. The reference is the **finite-time** full matrix, not the limiting orthogonal factor. |
| Newton | Start from the preceding accepted state. Stop when `||F(w)||∞≤10^-12(1+||w||∞)`; backtracking requires the candidate residual to decrease. A fixed-grid failure raises an error; an adaptive failure is retried from the last accepted state with half the step. |
| Independent oracle | SciPy Radau with `rtol=10^-12` and `atol=10^-14`. |
| Adaptive runs | Initial trial `h=0.15`, `atol=10^-8`, `rtol=10^-6`. Compare one full and two half steps; accept the fine value when the normalized estimate is at most one. This does not increase the base method's order or prove global error or stability. |
| Trajectory and rank deficiency | RK4 with `N=400` on `[0,2]`; rank-deficient initial singular values `(0,1.4,3)` with `N=1600` on `[0,8]`. |
| Matched-accuracy cost | `N=(160,17,160)` for Euler, RK4 and Implicit Euler. The three actual terminal errors are about `(9.21,8.85,9.32)×10^-4`, within 6% of one another. RHS evaluations are `(160,68,862)`. |

The model is nondimensional, and the regenerated PNGs are saved at 220 DPI.
Colour is paired with distinct markers or line styles where multiple methods
share an axis. The cost figure counts RHS calls only; Jacobian evaluations and Newton
iterations are listed separately. It does not include Jacobian assembly,
linear algebra factorization, Python overhead or plotting, so it is not a
wall-clock ranking. The Lyapunov identity panel uses a finite difference
along a numerical trajectory and the exact rate at the midpoint; its
nonzero residual reflects discretization. The reported *scaled* residual
divides by `max(1, |rate|)` and is not a pure relative error.


## Current report delivery

`report_v3/report.pdf` is the current integrated report. It contains the
abstract, Sections 1--6, references, and Appendices A--C.

The current core suite has 13 tests, covering model derivatives, convergence,
geometry, adaptivity and edge cases. The earlier 14-test bilingual run is a
[historical validation record](report_v3/checklist/VALIDATION_RUN_2026-10-03.md).
The advanced Gauss IRK4 checks live in `code_advanced/test_gauss_irk4.py`.

The earlier `report_v1/` and `report_v2/` directories are preserved as
historical snapshots. See the
[version index](notes/REPORT_VERSIONS.md) for version and recovery
information.
