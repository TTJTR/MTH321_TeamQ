# Report v3：完整报告 / Complete Report

日期：2026-10-02。

`report_v3/` contains the integrated final report for MTH321 Project 1.
It includes the abstract, Sections 1--5, references, and Appendices A--C.
`report_v1/` and `report_v2/` are retained as historical snapshots.

## 文件 / Files

| 路径 | 用途 / Purpose |
|---|---|
| `report.tex` | 完整报告编译入口，包含 Abstract、Sections 1--5、References 和 Appendices A--C。 |
| `report.pdf` | 当前完整报告 PDF。 |
| `sections/section1.tex` | Background：项目背景、极分解梯度流与研究动机。 |
| `sections/section2.tex` | Discretisation and Analysis：三种数值方法、误差、稳定性与收敛分析；Algorithm 1 为 Newton 伪代码。 |
| `sections/section3.tex` | Implementation：实现、参数、输出布局与 Algorithm 2 自适应伪代码。 |
| `sections/section4.tex` | Numerical Experiments：收敛、稳定性、自适应、成本、几何与秩亏实验。 |
| `sections/section5.tex` | Conclusions：主要数值结果、稳定性、成本比较与限制总结。 |
| `appendices/appendix_a.tex` | AI Transparency Log。 |
| `appendices/appendix_b.tex` | Individual Contribution Statements (ICS)。 |
| `appendices/appendix_c.tex` | 六份 CSV 与 JSON 的图映射、字段定义、数值摘录与复现说明。 |
| `references.tex` | 报告参考文献。 |
| `figures/` | 八张报告使用的 PNG 图。 |
| `data/` | 六份完整 CSV、`summary.json` 和数据说明。 |
| `checklist/README.md` | 项目与代码验收检查记录。 |
| `CHANGELOG.md` | v3 修改、整合与验证记录。 |
| `manifest.json` | 报告及对应数据、图片、代码和测试文件的 SHA-256 清单。 |

## 八张图 / Eight figures

| 图 | 用途 / Purpose | 数据 / Data |
|---|---|---|
| `convergence.png` | 完整矩阵误差与理论/拟合阶；order verification. | `convergence.csv` |
| `cost_accuracy.png` | 相近误差下 RHS 调用数；matched accuracy cost. | `cost_accuracy.csv` |
| `stability_regions.png` | 标量稳定域与初始谱；analytic stability regions. | 解析函数 + `summary.json` |
| `frozen_spectrum.png` | 初始谱和局部显式步长界；spectrum and local cutoffs. | `summary.json` |
| `stability_sweep.png` | 快方向放大和步长—误差；amplification and error sweep. | `stability_sweep.csv` |
| `trajectory_diagnostics.png` | 奇异值、能量、缺陷与残差；geometry and Lyapunov checks. | `trajectory.csv` |
| `adaptive_steps.png` | 三方法接受步长；accepted adaptive steps. | `adaptive_steps.csv` |
| `rank_deficient.png` | 零奇异值与部分等距极限；rank-deficient limit. | `rank_deficient.csv` |

详细字段见 [data/README.md](data/README.md) 和附录 C。  
实现说明：[中文](../README_ZH.md)、[English](../README_EN.md)。

## 编译与复现 / Build and reproduce

在本目录连续运行两遍 / Run twice from this directory:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error report.tex
pdflatex -interaction=nonstopmode -halt-on-error report.tex
```

在 Project1 下 / From Project1:

```powershell
python -m pip install -r requirements.txt
python -B code/run_all.py
python -B code_zh/run_all.py
python -B -m unittest discover -s test -v
```

代码只重建工作输出，不覆盖本版快照。
CSV、PNG、PDF 和 JSON 按原始字节校验；其他文本先统一换行到 LF，
使 Windows 与 Linux 检出时都能核对同一份 manifest。
整合正文时可以 input 各节，保留入口宏包与 graphicspath 图片路径。
独立入口的 setcounter 用于当前编号；小组最终主文档应按自己的章节顺序设置。
Reproduction does not overwrite archived snapshots. The team can include
the modular section files, carrying over required packages and figure paths.

恢复方法见 [版本索引](../notes/REPORT_VERSIONS.md)。
AI Transparency Log 已纳入当前版本；附录 B 收录五位成员各一页的 ICS，
封面列出对应姓名和学号。演示文件与最终代码 ZIP 仍按小组最终提交安排处理。
