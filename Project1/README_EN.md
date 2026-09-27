# MTH321 Project 1: Polar-Factor Gradient Flow

## Run the project

Use Python 3.10 or newer. In the `Project1` directory:
The recorded results were produced with Python 3.12.4, NumPy 1.26.4,
SciPy 1.13.1 and Matplotlib 3.8.4.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python code/run_all.py
.venv\Scripts\python code_zh/run_all.py
.venv\Scripts\python -m unittest discover -s report_v1/checklist -v
```

Each `run_all.py` rebuilds the PNG figures, CSV data and `summary.json` in its
own `figures/` directory. The two source trees are independently runnable:
`code/` has English comments and `code_zh/` has Chinese comments. Function
names, data columns and plot labels are shared so that results can be compared
and inserted into an English report. `summary.json` records the Python and
library versions used for each run.

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
| `code/run_all.py` | English command-line entry point; calls every experiment and prints the fitted orders and reference disagreement. |
| `code_zh/model.py` | Chinese-commented, independently runnable counterpart of `code/model.py`. |
| `code_zh/solvers.py` | Chinese-commented counterpart of `code/solvers.py` with the same numerical behavior. |
| `code_zh/experiments.py` | Chinese-commented counterpart of `code/experiments.py`; writes to `code_zh/figures/`. |
| `code_zh/run_all.py` | Chinese command-line entry point. |
| `report_v1/checklist/test_validation.py` | Checks the analytic Jacobian against finite differences, both full spectra, the energy identity, the diagonal scalar sanity case, the SVD/Radau comparison, convergence orders, adaptive behavior and the rank-deficient case. |
| `report_v1/checklist/test_bilingual_parity.py` | Runs both source trees separately and compares their model, fixed-step and adaptive numerical outputs. |
| `report_v1/checklist/README.md` | Code-only acceptance checklist, evidence, figure mapping and reproduction commands. |
| `requirements.txt` | Lists NumPy, SciPy and Matplotlib. |
| `CODE_HANDOFF.md` | Numbers and interpretation for integrating the code results into report Sections 3–4. |
| `report_v1/Section2Draft_v5.tex` | Corrected v5 theory/report with pseudocode matched to the completed implementation; compiles directly against the eight committed images in `report_v1/figures/`. |
| `slides/Topic5_presentation.tex` | Source for the 11-slide presentation draft; `slides/Topic5_presentation.pdf` is the compiled deck. |
| `CHANGELOG_V5.md` | Records each theory/code correction, reproducible evidence, and the team-specific items left for submission. |

## What each figure shows

The filenames below are generated under `code/figures/`. The Chinese code generates
the same filenames under `code_zh/figures/`. The eight report PNGs are committed under
`report_v1/figures/` so the LaTeX source builds without first running the code.
The English run's six CSV files and `summary.json` are committed as numerical
evidence; the Chinese run regenerates its own matching outputs locally.

| Figure | Meaning and companion data |
|---|---|
| `convergence.png` | Three log-log panels show terminal **full-matrix Frobenius error** against fixed step size, theoretical `h¹`/`h⁴` slopes, fitted lines and 95% regression bands. `convergence.csv` contains `N`, `h`, error, adjacent observed order and work counts. RK4's fit uses its finest three grids. The band is a descriptive least-squares diagnostic for deterministic data, not a probability statement about the ODE error. |
| `cost_accuracy.png` | Log-log **achieved error versus RHS evaluations** across several fixed grids for each method. Stars identify the three matched-error points near `9×10⁻⁴`; the grey band spans their actual errors. `cost_accuracy.csv` has all plotted points, `matched_point`, step counts, RHS/Jacobian evaluations and Newton iterations. See the cost caveat below. |
| `stability_regions.png` | Three panels show the analytic scalar-test regions `|R(hλ)|≤1` for Euler, RK4 and Implicit Euler. Shading comes from the stability functions, not from a nonlinear simulation. There is no companion CSV. |
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
