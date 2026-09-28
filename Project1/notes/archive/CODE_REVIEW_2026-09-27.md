> 历史记录：保留原日期与当时结论。当前交付见 [report_v2](../../report_v2/README.md)。

# Topic ⑤ 题目完成度复核

复核日期：2026-09-27。依据是 `D:\MTH321\课件\problem_pack.pdf` 第 8–9 页的 Topic ⑤ 原题，以及 `ODE_IVP_Project_Brief.pdf` 中适用于该扩展题的数值方法、稳定性、验证、自适应和成本要求。本文件**只判断题目要求是否由代码和报告完成**；不评价代码风格、依赖管理、文件打包或团队材料。复核对象为本地 [`report_v1/Section2Draft_v5.tex`](../../report_v1/Section2Draft_v5.tex)、两版代码和测试。

## 结论

**Topic ⑤ 的必做数学与数值任务已经完成。** 原先报告遗漏的“环境空间梯度流与正交群切向投影的区别”已补在第 2.1 节；原题给出的对角初值 sanity check 已加入自动测试。报告 PDF 重新编译后仍为 29 页，10 项测试全部通过。原题第 9 页的微波滤波器应用明确是可选扩展，未实现不影响本结论。

## 原题逐项核对

| 原题要求 | 判定 | 代码和报告证据 |
|---|---|---|
| 使用规定矩阵 ODE `X'=X(I-XᵀX)`，将矩阵向量化 | **完成** | [`code/model.py`](../../code/model.py) 的 `matrix_rhs`/`rhs` 与方程一致；`vectorize`、`unvectorize` 全程使用列优先 `vec(X)`，报告第 2.1 节说明。中文代码对应于 [`code_zh/model.py`](../../code_zh/model.py)。 |
| 运行三种必选方法：显式 Euler、RK4、一个隐式法及 Newton 解算 | **完成** | [`code/solvers.py`](../../code/solvers.py) 的 `_one_step` 实现三个单步格式；隐式 Euler 解完整残差 `w-y_n-hf(t+h,w)=0`，Newton Jacobian 为 `I-hJ_f`。报告第 2.1 节及 PDF 第 7 页 Algorithm 1 与代码对应。 |
| 用**完整有限时间矩阵精确解**验证三方法观测阶 | **完成** | `model.exact_matrix` 从初始 SVD 重建矩阵；[`code/experiments.py`](../../code/experiments.py) 的 `convergence` 以终点 Frobenius 误差拟合斜率 `1.010 / 3.927 / 1.014`，对应理论阶 `1 / 4 / 1`。`convergence.png/.csv` 和报告第 4.1 节均可核对，未以极限极因子代替有限时间解。 |
| 使用 `R(0.4) diag(0.2,1.4,3) R(-0.7)ᵀ`，写出区间、容差和步长 | **完成** | `model.benchmark()` 实现题设初值；报告与 [`README_EN.md`](../../README_EN.md)/[`README_ZH.md`](../../README_ZH.md) 记录主实验 `[0,2]`、固定网格、Newton 阈值 `10⁻¹²`，自适应 `atol=10⁻⁸`、`rtol=10⁻⁶`、初始试探步 `0.15`。 |
| 检查奇异值向 1 移动且不越过；检查数值 `Φ` 是否单调，并解释大步可能破坏性质 | **完成** | `trajectory_diagnostics.png/.csv` 和 `summary.json` 记录细网格 RK4 轨迹的单调性与无越过；`stability_sweep.csv` 显示大步的越过、能量增加或显式方法失败。报告第 4.2、4.4 节解释这些是步长相关的数值现象。 |
| 诊断 Lyapunov 恒等式与有限时间正交性缺陷 | **完成** | 轨迹图第 4 面板是离散恒等式残差；缩放最大残差约 `4.69×10⁻⁴`。终点数值缺陷 `0.305932824226` 与精确非零值 `0.305932824210` 对比；报告没有要求有限时刻达到机器零。 |
| 平衡点线性化，区分中性切向与收缩法向，并联系 `s₃(0)=3` 的快瞬态 | **完成** | 报告第 2.3 节给出三个零切向模态、六个 `-2` 法向模态；初始完整 Jacobian 谱含快模态 `-26`。`frozen_spectrum.png` 与 `stability_sweep.png` 将局部显式步长估计和非线性实际表现联系起来。 |
| 用秩亏初值再做实验，验证零奇异值，并解释部分等距极限 | **完成** | `rank_deficient.png/.csv` 使用 `(0,1.4,3)`，在 `[0,8]` 上数值零模态保持在约 `7.1×10⁻¹⁵` 以下；报告说明秩二极限是部分等距矩阵。 |
| 区分环境空间梯度流与正交群约束优化的切向投影 | **完成** | 报告第 2.1 节新加 `P_X(G)=G-X sym(XᵀG)=X skew(XᵀG)`，说明约束流 `X'=-P_X(G)`，以及 `(I-XXᵀ)G` 对方形正交 `X` 恒为零，不能充当所需投影。 |
| 对角初值 sanity check；一般初值从 SVD 重建精确矩阵 | **完成** | [`test/test_validation.py`](../../test/test_validation.py) 的 `test_diagonal_scalar_sanity_case` 对比独立标量公式、矩阵精确解和 RK4：在 `t=0.7`，解析矩阵与标量对角解差为 0，RK4 的非对角项为 0，终点矩阵误差约 `3.59×10⁻¹²`；一般初值另由 SVD/Radau 检查。 |

## Project Brief 中相关的共同要求

| 要求 | 判定 | 证据 |
|---|---|---|
| 三种方法的标量绝对稳定域由公式导出并绘制 | **完成** | 报告第 2.3 节给出 `R_E(z)=1+z`、RK4 四阶多项式、`R_I(z)=1/(1-z)`；`stability_regions.png` 按解析稳定函数作图。 |
| 给出系统特征值范围和显式步长限制；说明冻结 Jacobian 只是局部诊断 | **完成** | 初始谱、平衡谱、Euler `h≈0.0769` 和 RK4 `h≈0.1071` 的局部界限在报告和 `summary.json`；非线性扫步另作检验。 |
| 演示自适应步长且局部误差受控 | **完成** | 报告 PDF 第 19 页 Algorithm 2 对应 `solve_adaptive`；三个方法的接受步长发生变化，接受的最大归一化估计局部误差均小于 1；`adaptive_steps.png/.csv` 给出轨迹。 |
| 自建参考解，至少两种独立验证 | **完成** | 有限时间 SVD 公式与独立高精度 Radau 解在 `t=2` 相差 `1.16×10⁻¹³`；对角标量 sanity check 再检验模型和精确解。SciPy 仅作验证参考，不是被比较的三种自实现方法之一。 |
| 在匹配精度下比较明确的成本指标 | **完成** | 三方法终点误差约为 `(9.2066,8.8502,9.3194)×10⁻⁴`，相差约 5.3%；RHS 调用分别为 `160/68/862`。报告和成本图声明未计 Jacobian 组装、线性求解及运行时开销，没有把 RHS 次数误称为墙钟时间。 |

## 复核运行

- `python code/run_all.py`、`python code_zh/run_all.py`：均成功；八张报告图与英文入口重生图逐个 SHA-256 相同，中英文 `summary.json` 和八张同名 PNG 也相同。
- `python -B -m unittest discover -s test -v`：**10/10 通过**，包括对角初值测试、解析 RHS Jacobian 与完整隐式残差 Jacobian 的有限差分测试、三方法收敛阶、Radau 交叉验证、适应步长、能量/秩亏和中英文数值一致性。
- `report_v1/Section2Draft_v5.tex` 连续两次编译成功，PDF 为 **29 页**；未见未定义引用、缺图或 overfull 警告。

**范围说明：** 上述“完成”指 Topic ⑤ 和 Project Brief 的数学、算法、数值验证任务。团队姓名/ICS、代码 ZIP、演示批次等提交材料在 [`V1_DELIVERY_CHECKLIST.md`](V1_DELIVERY_CHECKLIST.md) 另行标注；它们不属于本次题目完成度判断。
