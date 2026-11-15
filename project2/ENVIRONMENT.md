# Established course environment and PINN extension

The course base environment is established and fixed by the team. Reuse it
for the classical FDM/FEM work; a fresh environment or changes to its NumPy,
SciPy and Matplotlib versions are not a submission requirement for this task.
`Project1/requirements.txt` uses those same three core libraries. The bounds
in this project's `requirements.txt` describe compatibility, not a request to
upgrade or replace the fixed course environment. `threadpoolctl` controls
numerical-library threads; the classical experiments record one BLAS thread.

From the existing local environment:

```text
conda activate dl
python -B code/run_all.py
```

## Recorded versions are provenance

The existing `dl` environment inspected on 2026-11-16 has Python 3.10.18,
NumPy 2.2.6, SciPy 1.15.3, Matplotlib 3.10.3 and threadpoolctl 3.6.0.
The archived classical timing record in
`algorithm_section/results/environment.json` records Python 3.10.18,
NumPy 2.2.6 and SciPy 1.15.3. These records are retained with their measurements.
Project 1's historical `data/summary.json` records a different run (Python
3.12.4, NumPy 1.26.4, SciPy 1.13.1, Matplotlib 3.8.4). A historical run record
is not a new instruction to change the established course baseline.

## Optional PINN extension

The advanced method adds PyTorch. CPU checkpoint replay has been exercised
with PyTorch 2.7.1+cpu in the existing `dl` environment. If PyTorch is missing,
`requirements-pinn.txt` specifies the tested 2.7.1 extension; preserve the
fixed base packages rather than rebuilding the course environment. PyTorch
is already installed in the validated local environment, so no installation
or environment change was performed for this revision.

The archived GPU training used PyTorch 2.8.0+cu128 and an A100-PCIE-40GB.
That training environment is separate from CPU checkpoint replay. The
training record and device claims remain unchanged. No retraining is required
to regenerate the report's comparisons from its archived checkpoints.

`pypdf` is an artifact-checking tool used by `code/check_artifacts.py`, not a
PDE solver dependency. pdfLaTeX/BibTeX are needed only for `--build-report`.
No independent fresh-machine installation was claimed or made a pending
course-baseline requirement. The evidence certifies the recorded executions.
