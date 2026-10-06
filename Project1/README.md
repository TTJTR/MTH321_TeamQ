# MTH321 Project 1: polar-factor gradient flow

The current integrated submission is [report_v3](report_v3/README.md). It contains the abstract, Sections 1–6, references, and Appendices A–C. Earlier [v1](report_v1/README.md) and [v2](report_v2/README.md) directories are historical snapshots.

## Reproduce

From `Project1/`, with Python 3.10 or newer:

```powershell
python -m pip install -r requirements.txt
python -B code/run_all.py
python -B -m unittest discover -s test -v
python -B code_advanced/test_gauss_irk4.py
python -B code_advanced/run_comparison.py
```

The baseline command writes eight figures to `figures/`, six CSV files and `summary.json` to `data/`. The advanced command writes four comparison figures and two CSV files plus a JSON summary in their `advanced_irk4/` subdirectories. The report bundles its own snapshots, so these commands do not overwrite the submitted evidence.

## Layout

| Path | Purpose |
|---|---|
| `code/` | Baseline model, explicit Euler, classical RK4, implicit Euler and experiments. |
| `code_advanced/` | Two-stage Gauss implicit RK4, advanced comparison and its dedicated checks. |
| `test/` | Core numerical validation (13 tests). |
| `data/`, `figures/` | Regenerated working results. |
| `report_v3/` | Current LaTeX source, PDF, submitted figures/data, checklist and manifest. |
| `report_v1/`, `report_v2/` | Preserved historical report snapshots. |
| `notes/REPORT_VERSIONS.md` | Version and Git recovery notes. |

For each code file, figure, numerical setting and output field, see the [detailed implementation guide](README_EN.md) and the [advanced method guide](code_advanced/README.md). The 2026-10-03 bilingual reproduction record remains in Git history and the report checklist as a historical record; the current delivery has one English source tree.
