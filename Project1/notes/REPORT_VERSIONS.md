# Report versions and recovery

| Version | Directory | Role |
|---|---|---|
| v1 | [report_v1](../report_v1/README.md) | Preserved initial report snapshot; Git tag `report-v1`. |
| v2 | [report_v2](../report_v2/README.md) | Preserved Sections 2–4 and Appendix C snapshot; Git tag `report-v2`. |
| v3 | [report_v3](../report_v3/README.md) | Current complete report with Sections 1–6. |

The directories make earlier PDFs directly accessible. Git history and tags also recover the matching code and test files. Routine edits to the current report should update `report_v3/`; a new version directory is needed only for a deliberate frozen snapshot.

```powershell
git log --oneline --decorate
git tag --list
git show report-v1:Project1/report_v1/Section2Draft_v5.tex
```
