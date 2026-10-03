# MTH321 Project 1 — Topic ⑤

当前完整报告为 [report_v3](report_v3/README.md)，包含 Abstract、Sections 1--5、References 和 Appendices A--C。

[report_v1](report_v1/README.md) 和 [report_v2](report_v2/README.md) 原样保留，作为历史版本。

版本、Git 标签和恢复方法见 [版本索引](notes/REPORT_VERSIONS.md)。

Current complete report: [report_v3](report_v3/README.md), containing the Abstract, Sections 1--5, References, and Appendices A--C.

The previous `report_v1/` and `report_v2/` directories are preserved as historical snapshots. See the version index for recovery information.

## 运行 / Run

在本目录运行 / Run from this directory:

```powershell
python -m pip install -r requirements.txt
python -B code/run_all.py
python -B code_zh/run_all.py
python -B -m unittest discover -s test -v
```

## 目录 / Layout

| 目录 | 用途 / Purpose |
|---|---|
| `code/` | 英文注释源码；English source only. |
| `code_zh/` | 中文注释的独立源码；independent Chinese source. |
| `test/` | 两份验证脚本，共 14 项测试。 |
| `data/` | 当前运行生成的六份 CSV 与 `summary.json`；含字段说明。 |
| `figures/` | 当前运行生成的八张 PNG 工作图。 |
| `outputs_zh/` | 中文入口独立输出。 |
| `report_v1/` | 保留的早期报告快照。 |
| `report_v2/` | 保留的 Sections 2--4 与 Appendix C 章节交付版本。 |
| `report_v3/` | 当前完整报告，包含 Sections 1--5、Appendices A--C、图、数据、checklist 与 manifest。 |
| `notes/` | 版本索引与历史材料。 |
| `slides/` | 小组演示文件。 |

完整说明：[中文 README](README_ZH.md)、[English README](README_EN.md)。

当前报告说明：[report_v3 README](report_v3/README.md)。  
修改记录：[v3 CHANGELOG](report_v3/CHANGELOG.md)。  
验收证据：[v3 checklist](report_v3/checklist/README.md)。
最新独立复现记录：[2026-10-03 validation run](report_v3/checklist/VALIDATION_RUN_2026-10-03.md)。
