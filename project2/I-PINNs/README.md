# I-PINNs — Project 2 interface experiments

Directory requested by the team: `project2/I-PINNs/`.

**Execution status: running — this is an interim snapshot.**

This implementation is a generic interface-aware PINN baseline with two subdomain networks and soft solution/flux constraints. It is **not yet verified as a full reproduction of the published I-PINNs architecture**.

- `src/`, `tests/`, `configs/`: numerical methods, independent checks and reproducible configurations.
- `runs/`: original configurations, environment/source hashes, raw NPZ arrays, model checkpoints, training logs, metrics and plots.
- `local_validation/`: original CPU smoke-test data and controls.
- `comparison.csv`, `comparison_summary.json`, `comparison.png`, `SERVER_REPORT.md`: final cross-seed summaries (available after completion).
- `server_results.zip`, `download_manifest.json`: packaged server artifacts and checksums (available after completion).
- `EXPERIMENT_README.md`: detailed equations, norm definitions, commands and limitations.

Actual server GPU reported by CUDA: NVIDIA A100-PCIE-40GB. The team initially described the rental as V100; metadata records the detected hardware.

The standard smooth FDM benchmark checks second-order convergence. The layered benchmark is piecewise linear and y-independent; harmonic FDM can reach round-off. PINN completion is not a convergence certificate. Failed accuracy checks are retained. The single-network baseline has fewer parameters, so equal training budgets are not equal model capacities.

All generated experiment artifacts are included; caches and connection/authentication metadata are excluded. Original course PDFs are not part of this code/results package.
