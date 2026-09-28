# English source

Run `python -B code/run_all.py` from `Project1/` after installing
`requirements.txt`. PNGs go to project-level `figures/`; CSV/JSON files go
to `data/`. This directory contains source only.

| File | Purpose |
|---|---|
| `model.py` | Benchmark, matrix/vector conversion, RHS, analytic Jacobian, finite-time SVD solution and diagnostics. |
| `solvers.py` | Three methods, damped Newton, fixed/adaptive drivers and work counts. |
| `experiments.py` | All experiments, eight figures, six CSVs and the JSON summary. |
| `run_all.py` | Selects output paths and runs every experiment. |

Details: [English README](../README_EN.md).
Current chapters: [report_v2](../report_v2/README.md).
Running the code does not overwrite report snapshots.
