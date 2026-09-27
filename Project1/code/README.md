# Numerical code / 数值代码

From `Project1/`, install `requirements.txt` and run `python code/run_all.py`.
It regenerates eight figures, six CSV datasets and `summary.json` under
`code/figures/`. All paths are relative to the source files.

在 `Project1/` 安装 `requirements.txt` 后运行 `python code/run_all.py`；
程序会在 `code/figures/` 重建八张图、六份 CSV 和 `summary.json`。

| File | Role / 作用 |
|---|---|
| `model.py` | Matrix flow, Jacobian, exact SVD solution and diagnostics / 矩阵方程、Jacobian、精确解与诊断 |
| `solvers.py` | Euler, RK4, Implicit Euler, Newton and step doubling / 三种积分法、Newton 与自适应步长 |
| `experiments.py` | Benchmarks, tables, figure generation and summaries / 数值实验、图表与摘要 |
| `run_all.py` | One-command entry point / 一键运行入口 |

See [English README](../README_EN.md) or [中文 README](../README_ZH.md)
for the purpose of **each figure** and the matching data file. The eight
PNG files used in the report are also committed in
[`../report_v1/figures/`](../report_v1/figures/).
