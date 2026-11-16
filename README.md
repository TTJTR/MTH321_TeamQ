# MTH321 — Team Q

Numerical analysis coursework, reports and reproducible experiments.

| Project | Report | Documentation |
|---|---|---|
| Project 2: variable diffusion and material interfaces | [Team Q report](project2/report/MTH321_Project2_TeamQ_Report.pdf) | [Project 2 README](project2/README.md) |
| Project 1: polar-factor gradient flow | [Current report source and files](Project1/report_v3/README.md) | [Project 1 README](Project1/README.md) |

## Project 2 quick start

Use the team's established course environment. From the repository root:

```text
conda activate dl
cd project2
python -B code/run_all.py
```

This runs production checks, regenerates the classical figures from archived
data, replays six neural checkpoints on CPU and regenerates all nine external
report figures. It does not retrain the networks. Use `--recompute` to rerun
classical experiments and `--build-report` to also build the report with
pdfLaTeX/BibTeX. See the [full commands](project2/README.md),
[environment notes](project2/ENVIRONMENT.md) and
[checklist](project2/reviews/CHECKLIST_STATUS.md).
The assessed [code review by Meichen Ding](project2/reviews/CODE_REVIEW_2026-11-15.md)
is included in the Project 2 submission materials.

## Project 1

The current integrated Project 1 delivery is `Project1/report_v3/`.
Earlier report versions are preserved as historical snapshots. Follow the
[Project 1 instructions](Project1/README.md) for its run commands and
[version index](Project1/notes/REPORT_VERSIONS.md) for provenance.
