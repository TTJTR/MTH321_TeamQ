# Report v2：第 2–4 节与附录 C / Sections 2–4 and Appendix C

日期：2026-09-28。仅完成第 2、3、4 节和附录 C，供小组整合到最终报告。
第 1、5 节不在本次工作范围；`report_v1/` 原样保留。
This is a chapter delivery, ready for team integration.

## 文件 / Files

| 路径 | 用途 / Purpose |
|---|---|
| `report.tex` | 独立编译入口，编号 2、3、4、C。 |
| `report.pdf` | 本版章节 PDF。 |
| `sections/section2.tex` | 理论、三方法分析、稳定性证明；Algorithm 1 为 Newton 伪代码。 |
| `sections/section3.tex` | 实现、参数、输出布局；Algorithm 2 为自适应伪代码。 |
| `sections/section4.tex` | 收敛、稳定性、自适应、成本、几何、秩亏实验；11 项验证。 |
| `appendices/appendix_c.tex` | 六份 CSV 与 JSON 的图映射、字段定义、摘录与复现。 |
| `references.tex` | 本次章节的参考文献。 |
| `figures/` | 八张 220 DPI PNG。 |
| `data/` | 六份完整 CSV、summary.json 和双语字段说明。 |
| `checklist/README.md` | 课程清单验收证据。 |
| `CHANGELOG.md` | 改动、修复和验证记录。 |
| `manifest.json` | 报告与对应代码/测试的 SHA-256 清单；文本换行统一 LF 后计算。 |

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
CSV、PNG 和 PDF 按原始字节校验；其他文本先统一换行到 LF，
使 Windows 与 Linux 检出时都能核对同一份 manifest。
整合正文时可以 input 各节，保留入口宏包与 graphicspath 图片路径。
独立入口的 setcounter 用于当前编号；小组最终主文档应按自己的章节顺序设置。
Reproduction does not overwrite archived snapshots. The team can include
the modular section files, carrying over required packages and figure paths.

恢复方法见 [版本索引](../notes/REPORT_VERSIONS.md)。
团队身份、AI Log、ICS、演示与最终代码 ZIP 不由本次章节交付声明完成。
