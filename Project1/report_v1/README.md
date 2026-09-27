# Topic ⑤ report_v1 / 报告交付目录

This directory contains the current report and the evidence needed to build
and check it. 本目录只保留当前报告及其必要的图片、代码验收资料。

| Item / 文件 | Purpose / 用途 |
|---|---|
| `Section2Draft_v5.tex` | Editable LaTeX source / 可编辑报告源码 |
| `Section2Draft_v5.pdf` | Compiled 29-page report / 已编译的 29 页报告 |
| `figures/` | The eight PNGs cited by the LaTeX source / 正文引用的八张图 |
| [`checklist/`](checklist/README.md) | Code-only checklist and two runnable verification scripts / 代码清单及两个验证脚本 |

The figures come from `../code/run_all.py` at 220 DPI. To rebuild the PDF,
run twice from this directory / 图片由该入口生成；在本目录运行两次：

```powershell
pdflatex -interaction=nonstopmode -halt-on-error Section2Draft_v5.tex
pdflatex -interaction=nonstopmode -halt-on-error Section2Draft_v5.tex
```

LaTeX creates `.aux`, `.log`, `.out`, and `.toc` files. They are ignored by Git
and can be removed after compilation / 这些是可删除的编译缓存：

```powershell
Remove-Item -LiteralPath Section2Draft_v5.aux,Section2Draft_v5.log,Section2Draft_v5.out,Section2Draft_v5.toc -ErrorAction SilentlyContinue
```

| Figure / 图片 | Purpose / 用途 |
|---|---|
| `convergence.png` | Full-matrix errors, theoretical orders and fitted slopes / 完整矩阵误差、理论阶与拟合阶 |
| `stability_regions.png` | Three scalar stability regions and initial modes at `h=0.08` / 三种稳定域与初始谱点 |
| `frozen_spectrum.png` | Initial Jacobian spectrum and local explicit-step limits / 初始谱与局部显式步长界 |
| `stability_sweep.png` | Nonlinear fast-mode amplification and terminal error / 非线性快模态放大与终点误差 |
| `adaptive_steps.png` | Accepted step lengths under step doubling / 自适应接受步长 |
| `trajectory_diagnostics.png` | Singular values, energy, orthogonality and Lyapunov residual / 奇异值、能量、正交性和 Lyapunov 残差 |
| `cost_accuracy.png` | Error versus counted RHS calls / 误差与 RHS 调用次数 |
| `rank_deficient.png` | Zero singular mode and partial-isometry limit / 零奇异模态与部分等距极限 |

For the code files and CSV columns, see [English](../README_EN.md) or
[中文](../README_ZH.md). 代码文件及 CSV 数据列的说明见对应语言的 README。
