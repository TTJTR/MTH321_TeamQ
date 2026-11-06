# 与 Method 部分的合并说明

## 合并位置

将 `algorithm_section.tex` 作为第 3 节放在 Method 的 `Discretisation and Analysis` 之后、`appendix` 之前。正文自带 `\section`，独立阅读版通过 `\setcounter{section}{2}` 显示为第 3 节。主报告中按已有节号顺序插入即可。

复制 `figures/`、`tables/` 和`src/` 代码目录到主报告目录，保持相对路径。加入 `\input{algorithm_section}`，并将本包 `refs.bib` 中的 `projectbrief`、`problempack` 两条合并到团队参考文献文件。其余引用沿用提供的文献键。

本包包含实际验证证据。正式报告的结果章可复用对应图片和 CSV，避免在不同章节重复放图。

## 本次已实现的范围

- FDM 采用共享面系数、稀疏组装和强 Dirichlet 消元。
- FEM 采用二维 P1 三角形单元及显式数值积分。
- 光滑问题使用相同网格、自由度、误差评价与 Jacobi-CG 容差，并和独立 SuperLU 解比较。
- 分层 FDM 与 FEM 分别使用奇数、偶数区间数，明确记录网格差异。
- 所有图表来自实际 CPU 运行，保存环境与时间，包含条件数估计、实际迭代次数及容差收紧。

## Method 中需要同步的表述

1. **FEM 的界面通量。** 将“conforming discretisation automatically enforces interfacial flux continuity”改为“the continuous weak problem implies flux continuity; the Galerkin method enforces the weak equations on its finite-dimensional test space, while the raw P1 flux can have jumps”。本分层精确解恰好属于界面对齐的 P1 空间，通量近精确来自该算例的特殊性。

2. **奇偶网格。** 保留本实验的奇数 FDM、偶数 FEM 设置。关于“偶数 FDM 时两种节点平均自动相同”的论述需补充面系数的构造约定，界面节点 a(1/2) 的取值会影响简单的节点平均。

3. **算术平均的通量诊断。** 算术平均也保留共享面通量的离散守恒。此次 c=10、N=63 的实际数据中，两侧纯介质边上重构的通量差接近舍入误差，但共享界面通量相对于精确值的最大误差约为 0.662。应同时报告通量准确度和明确规定的跳跃诊断。将精确解代入错误面系数时的局部 O(1) 缺陷，需要与求解后数值通量的实际表现区分。

4. **相同容差与代数误差。** 相同 rtol 提供统一的停止设置；每个网格还通过直接解差验证代数误差确实小于测量的离散误差。使用本文中的容差收紧表支撑这一点。

5. **“sharp constant”用词。** Method 的二维谱下界 `lambda_min >= 8 a_min` 是可用的统一界。对 N≥2 的二维网格，“sharp”需要额外论证；建议直接称为 uniform bound。最大范数的 1/(8 a_min) 是所给屏障得到的二维上界，其可达性讨论需与一维情况区分。

6. **Taylor 余项与光滑性。** Method 中使用 C³ 系数、C⁴ 解，却在若干中间式使用 O(h⁵)、O(h⁴) 的更高阶余项。若保留这些具体展开，应提高相应光滑性假设并逐项核对余项；也可改写成直接证明二阶一致性所需的积分余项形式。本文的实际光滑基准是解析函数，具备充足光滑性。

7. **数值证据的来源。** Method 提到 `verify/check_stability.py` 及某些一维反例数值，但此次仅收到 tex/bib/pdf。该脚本及其数值尚未在本包复现。团队应补上原脚本和结果，或调整相关数值断言。算法包中的特征值和条件数记录只支撑本包实际测试的矩阵。

8. **界面 PINN。** 原有进阶实验保持自己的数据和说明。当前实现是两个独立 tanh 网络的 interface PINN 基线。写作时保留这一架构说明及参数量差异。

## 供团队 AI 日志使用的核验节点

- 手工 N=3 的 4×4 矩阵与代码逐项一致；检查 y-fast 排序。
- 界面行使用 -N²×20/11，边界项使用实际面系数。
- 通过独立通量差分确认光滑制造源项。
- 通过线性 patch 检查 FEM 梯度、局部矩阵和组装。
- 增加求积阶数后，代表性 FEM 载荷和共同误差积分保持一致。
- 比较三个 CG 容差与直接解，并在每个光滑网格检查代数误差比例。
- 核对特征对残差、通量误差和离散极值范围。

以上为实际脚本提供的核验路径，团队成员需记录自己的执行与审核结果。
