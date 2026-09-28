# MTH321 Project 1 — Topic ⑤

当前交付为 [report_v2](report_v2/README.md)：第 2、3、4 节和附录 C。
本次不编写第 1、5 节，供小组整合到最终报告。
[report_v1](report_v1/README.md) 原样保留。
版本、Git 标签和恢复方法见 [版本索引](notes/REPORT_VERSIONS.md)。

Current delivery: Sections 2–4 and Appendix C, ready for team integration.
The previous report_v1 is preserved. See the version index for recovery.

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
| `test/` | 两份验证脚本，11 项测试。 |
| `data/` | 当前运行的六份 CSV 与 summary.json；含字段说明。 |
| `figures/` | 当前运行的八张 PNG，工作图不提交到 Git。 |
| `outputs_zh/` | 中文入口独立输出，不提交到 Git。 |
| `report_v1/` | 保留的上一版报告和图。 |
| `report_v2/` | 本次 PDF、LaTeX、八图、七份数据、清单和修改记录。 |
| `notes/` | 版本索引、历史材料；早期 report 草稿在 archive 中。 |
| `slides/` | 既有小组演示文件，本次不更新。 |

完整说明：[中文 README](README_ZH.md)、[English README](README_EN.md)。
修复记录：[v2 CHANGELOG](report_v2/CHANGELOG.md)。
验收证据：[v2 checklist](report_v2/checklist/README.md)。
