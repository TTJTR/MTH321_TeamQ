# Project 2 第三题 · 算法部分交接包

本包接在提供的 `Method(1).tex` 后，补全英文算法说明、伪代码、实际代码、图片和可复现实验。实现保守 FDM，并按 Method 中选定的路线加入二维 P1 FEM 对比。接口 PINN 的已有训练材料可在团队主报告中另行引用。

## 交给写作同学的文件

- `Algorithm.pdf` 为独立阅读版。
- `algorithm_section.tex` 为可合并的正文，内容从 Section 3 开始。
- `Algorithm.tex` 为独立编译入口。
- `refs.bib` 包含提供的参考文献及新增的两条课程资料引用。
- `figures/` 包含 6 张图，每张有 PDF 和 PNG。
- `tables/` 包含从实际 CSV 自动生成的 4 张 LaTeX 表。
- `integration_notes_zh.md` 说明与 Method 的衔接、需修改的表述及引用方式。

## 一键运行

在本目录执行，使用已有的 conda `dl` 环境。

```bash
conda activate dl
python -m pip install -r requirements.txt
python -B run_all.py
```

使用 CPU 和 float64，数值库线程限制为 1，无需服务器。脚本先运行数值测试，再重算数据和所有图表。设置在 `config.json`。运行时间随机器变化，`results/run_status.json` 中 `complete=true` 表示本次数据计算完成。脚本会重新生成 `results/`、`tables/` 和 `figures/` 中的实验产物。

如只需使用已保存的数据重绘，执行 `python -B make_figures.py`。图中的成本来自实际本地运行，重绘时保持这些计时值；完整重算会重新测量时间。

## 实现与学校要求

| 要求 | 对应内容 |
|---|---|
| 保守五点格式、边界数据组装 | `src/discretisation.py` 的 `assemble_fdm` |
| 二维 P1 弱形式、空间、积分、边界消元 | 同文件的 `mesh`、`triangle_quadrature`、`assemble_fem` |
| 有理由的稀疏求解器与停止准则 | `src/solvers.py`，CG/Jacobi 和独立 SuperLU |
| 光滑源项独立检查、四网格误差和阶 | `tests/test_numerics.py`、`results/smooth.csv` |
| 代数误差与离散误差分离 | `results/tolerance_sweep.csv`，同一矩阵上的容差收紧 |
| 分层算术/调和对比与通量 | `results/layered.csv`，`fig04_interface` |
| 对称性、SPD、极值界限 | 小网格特征值测试、矩阵诊断和分层数值界限检查 |
| 条件数、网格/反差影响 | `results/conditioning.csv`，显式特征对残差及 CG 次数 |
| 同问题的深度比较与成本 | 光滑 FDM/FEM 同网格、同求解器、同范数；`timing_repeats.csv` |
| 代码及图表复现 | `run_all.py`、依赖文件及运行环境/源码哈希记录 |

FDM 的数学模型、精确解和共享面格式沿用已完成的界面 PINN 基线，矩阵组装改为 NumPy 批量操作。P1 FEM 使用显式的二维三角形单元组装，依赖 NumPy/SciPy，团队可直接检查并修改每个局部矩阵。

## 数据口径

- 光滑网格为 N=16、32、64、128，N 表示每轴区间数，内点数 n=N-1，两种方法的自由度均为 n²。
- 分层 FDM 使用奇数 N=31、63、127、255，界面对齐 FEM 使用偶数 N=32、64、128、256。分层场的材料比为 10，外边界全部使用同一精确解。
- 条件数和迭代数实验使用 N=15、31、63，材料比 c=1、10、100。边界数据随 c 对应的精确解改变。
- `l2_nodal` 为内部节点面积加权误差，`linf_nodal` 为共同节点最大误差。
- `l2_common` 将两种方法的节点值都用同一个三角剖分作 P1 插值，再用相同规则积分。此值用于光滑问题的方法比较。分层 FDM 的普通 P1 插值跨过界面，因此即使节点值精确，连续插值误差仍可非零。
- `interface_flux_error` 为界面数值通量相对于精确通量的最大误差。`reconstructed_flux_jump` 的 FDM 定义为界面两侧最近纯介质网格边上通量之差，FEM 定义为实际相邻三角形上的法向通量差，二者定义及采样位置已在正文说明。
- CG 在退出后复算显式残差，必要时执行残差修正。CSV 保留请求容差、实际残差、代数解差和修正次数。诊断性残差历史的额外计算不计入主实验时间。
- 成本分开记录组装、Jacobi 设置、CG、LU 分解和三角求解。表中给出 3 次重复的各阶段中位数；原始重复值保存在 CSV。

## 编译 PDF

```bash
pdflatex -interaction=nonstopmode -halt-on-error Algorithm.tex
bibtex Algorithm
pdflatex -interaction=nonstopmode -halt-on-error Algorithm.tex
pdflatex -interaction=nonstopmode -halt-on-error Algorithm.tex
```

用 pdfLaTeX 编译，依赖常见的 amsmath、bm、graphicx、booktabs、algorithm、algpseudocode、listings、hyperref 等包。正文图表已随包附上。

## AI 与团队审核

代码、验证、图表和文字使用 AI 辅助完成。团队需亲自运行并复核，再将实际审核人、改动和复现数值填写到课程 AI Transparency Log 与个人 ICS。`integration_notes_zh.md` 中列出可供核验的具体检查。个人签名和贡献归属由实际参与成员填写。
