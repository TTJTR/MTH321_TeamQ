# Local verification — 2026-10-29

Status: framework smoke test passed. Server-scale experiments have not been run.

Environment: conda `dl`, Python 3.10.18, PyTorch 2.7.1+cpu, NumPy 2.2.6, SciPy 1.15.3. No CUDA is available in this environment. Existing environment was not modified.

## Checks performed

`python -m unittest discover -s tests -v`: all 6 checks passed:

1. Smooth FDM refinement approaches order 2; independent tight CG agrees with direct solution; smallest eigenvalue positive on a representative grid.
2. Layered harmonic FDM exact nodal reproduction, physical interface flux, matrix symmetry, off-diagonal signs, backward residual and maximum principle, for contrasts 1/10/100. Arithmetic contrast-10 comparison has visible nonzero error.
3. Explicit left-interface row on N=7 matches -(20/11)/h^2 east coupling, diagonal (3+20/11)/h^2 and the stated indexing.
4. Smooth manufactured source checked against automatic differentiation of analytic u and a.
5. Exact analytic branches substituted independently into all interface losses. Both one-sided derivative traces must be evaluated separately: using a global `where` formula exactly on the interface would select the same derivative for both sides.
6. Full training objective's parameter gradient checked against centred finite differences at eps=1e-4,1e-5,1e-6.

During development the analytic test oracle initially evaluated the same branch at the interface for both traces. This test-oracle defect was corrected before accepting the checks; the branch-specific model and independent FDM checks now agree. An earlier no-parameter test model also exposed a loss-initialization assumption, fixed by allocating the zero scalar from the sample tensor.

## Measured outputs

Smooth FDM, arithmetic faces:

| N | nodal Linf | observed interior L2 order |
|---|---:|---:|
|15|3.631e-3|—|
|31|8.530e-4|2.0024|
|63|2.066e-4|2.0006|
|127|5.086e-5|2.0001|

Layered c=10: harmonic nodal Linf is 1.44e-15 to 2.57e-14 across those grids; arithmetic nodal Linf decreases from 3.95e-2 to 4.78e-3. Do not fit convergence slopes to the harmonic round-off floor.

PINN: seed 42, c=10, float64 CPU, 800 Adam steps + budget of 100 L-BFGS iterations:

| Metric | interface-aware (1394 parameters) | single smooth network (697 parameters) |
|---|---:|---:|
|relative L2|6.631e-4|3.452e-1|
|nodal Linf|2.029e-3|5.286e-1|
|interface value jump max|1.145e-3|0 (structural)|
|interface flux jump / exact flux magnitude|4.927e-3|8.088e-1|
|training time, seconds|4.85|5.64|

The interface model passes configured smoke thresholds; the single model does not. Its unsuccessful result is retained and explicitly reported. These are one-seed, unequal-parameter-budget short runs. They do not establish a general method ranking. The single-network trial was launched with default result-recording mode, so its process can return zero while `accepted=false`; use `--require-acceptance` to make accuracy failure a nonzero exit.

Output evidence: `runs/local_smoke`, `runs/local_single`, `runs/local_smooth_fdm`. Each includes resolved config, predictions written before solves and source hashes. Solution/error heatmaps were visually inspected; the interface is at x=0.5, axes and colourbars are legible.

## AI solver audit (developer self-check, NOT student sign-off)

| Gate | Evidence and scope |
|---|---|
|1 transcription|problem.py equations and exact solutions match the smooth/layered specification; flux normal explicitly +x; analytic forcing checked independently with autograd.|
|2 structure/indexing|explicit nonstandard-row test; Dirichlet elimination; positive shared faces; symmetry/sign checks; documented C-order map.|
|3 linearisation|FDM is linear, no Newton Jacobian. Neural training derivatives checked by finite differences. Optimizer budgets and validation status recorded; reaching a budget is not called convergence.|
|4 independent reproduction|analytic exact solutions, second-order smooth refinement, exact layered physical flux and tight independent CG checks. PINN compared against analytic solution on held-out points.|
|5 interrogation|three hazards checked: residual vs solution error (both reported), wrong one-sided derivative trace (branch-specific oracle), incorrect interface resistance despite symmetric matrix (arithmetic control). More seeds, PINN sampling/weight studies and team review remain pending.|

The team must independently understand and verify the equations, boundary rows and checks before using these numbers in a report. This document does not claim an independent human/team audit.

## Outstanding limits

- This is a generic interface-aware PINN implementation, not yet verified as an exact reproduction of the named I-PINNs paper.
- No GPU execution, large contrast training sweep, statistical study, PINN convergence study, or ML novelty claim has been validated.
- Source packaging excludes raw runs; reproduce with the documented commands, or copy runs separately for full local artifacts.
