# 中文注释源码

在 `Project1/` 安装 `requirements.txt` 后运行
`python -B code_zh/run_all.py`。图片到 `outputs_zh/figures/`，
CSV/JSON 到 `outputs_zh/data/`。本目录只放源码，两版数值行为一致。

| 文件 | 用途 |
|---|---|
| `model.py` | 初值、矩阵/向量转换、右端、解析 Jacobian、精确解和诊断。 |
| `solvers.py` | 三方法、阻尼 Newton、固定/自适应驱动和工作量。 |
| `experiments.py` | 所有实验、八图、六份 CSV 和 JSON。 |
| `run_all.py` | 选择独立输出目录并运行全部实验。 |

详见 [中文 README](../README_ZH.md) 和 [report_v2](../report_v2/README.md)。
运行不会覆盖已归档报告。
