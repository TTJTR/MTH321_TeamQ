> 历史审查，保留原结论；当前状态见 [report_v2](../../report_v2/README.md)。

# 课程 PDF 与 GitHub 理论稿交叉核对（2026-09-27）

核对范围：`D:\MTH321\课件` 中 15 份 PDF 均已盘点；数学核对重点为
`lecture1_slides.pdf`、`lecture2_slides.pdf`、`Week 2 Supplementary.pdf`、
`Tutorial2_supplementary.pdf`、`Tutorial3_Suplementary.pdf`、
`ODE_IVP_Project_Brief.pdf`、`problem_pack.pdf`。GitHub 对象为
`Project1/notes/theory_section2_schemes.md`、
`Project1/notes/theory_section2_adaptive.md` 及
`Project1/report/Section2Draft_.tex`（`main`，核对时读取）。以下页码为 PDF 阅读器
显示的页序，从 1 开始；`lecture2_slides.pdf` 的部分印刷页码与 PDF 页序不同。

## 核对结论

| 主题 | 课程依据 | 对 GitHub 稿件的判断与操作 |
|---|---|---|
| Euler、RK4、隐式 Euler 格式及稳定函数 | `lecture1_slides.pdf` PDF p. 10, 12；`lecture2_slides.pdf` PDF p. 4–5, 8；`Week 2 Supplementary.pdf` PDF p. 8 | `schemes.md` 的三个更新格式、RK4 稳定多项式及隐式 Euler 的 `1/(1-z)` 与课程一致，保留。 |
| “局部截断误差”两种记法 | `lecture1_slides.pdf` PDF p. 10 把除以 `h` 的 Euler 缺陷叫 LTE，量级 `O(h)`；`Week 2 Supplementary.pdf` PDF p. 6 把未除以 `h` 的一步缺陷写为 `O(h^(p+1))`，并说明有些书会除以 `h` | 两份课件只是术语约定不同。`schemes.md` §1.6 同时定义 `d` 和 `d/h`，基本正确。建议报告始终写清是“未归一化缺陷”还是“除以 h 的 LTE”。 |
| 隐式 Euler 的单步缺陷 | `Tutorial3_Suplementary.pdf` PDF p. 11 把精确解代入隐式公式所得的 `d=-h²y''(t+h)/2+O(h³)` 叫“单步缺陷” | `schemes.md` §3.7 采用这一名称符合课件；本次已修正先前审计中过重的术语批评。其 `-h²y''(ξ)/2+O(h³)` 混合了精确 Lagrange 余项和渐近展开，应改成 `-h²y''(ξ)/2`，或 `-h²y''(t+h)/2+O(h³)`。若要称它为实际的一步数值解误差，还需说明两者的关系。 |
| 步长加倍后的阶数 | `Tutorial2_supplementary.pdf` PDF p. 23 明言“两个半步仍是一阶方法”；p. 24 给出粗/细一步误差展开 | `adaptive.md` §8.1 声称只接受 `y_f` 就“提高一阶”，**与课件直接冲突**。接受 `y_f` 可减小误差常数，原方法全局阶仍为 `p`。若要消掉主导一步误差，另用 `y_ext=y_f+(y_f-y_c)/(2^p-1)`，并注明额外条件。其 §4 对 `y_f` 的估计式 `(y_f-y_c)/(2^p-1)` 本身正确。 |
| 误差控制和稳定性 | `Week 2 Supplementary.pdf` PDF p. 10 写明 `hλ` 在稳定域内不证明非线性稳定；p. 16 写明局部误差指标不是全局误差或稳定性的证明；`lecture2_slides.pdf` PDF p. 19 专门询问 A-稳定性的适用范围 | `adaptive.md` §7 中“必然拒步直到进入稳定域”错误；§5 中 `E≤1` 对真实局部误差的“严格控制”也过满。改为控制**估计值**，并通过步长扫描或扰动实验验证稳定性。`schemes.md` §3.8 的“无条件无数值发散风险”也应限定为线性测试方程的左半平面模态。 |
| 步长加倍成本 | `Tutorial2_supplementary.pdf` PDF p. 23 明确每次试探有三个隐式求解；p. 27 要求统计被拒步和 Newton 更新；`ODE_IVP_Project_Brief.pdf` PDF p. 2 要求先说明成本量度、匹配误差再比较 | `adaptive.md` §8.3 先写 3 次评估，后称“计算量翻倍”，不准确。与单个固定步对比，是 3 个基础步/试探；还须计入拒步。实际墙钟时间或 RHS 次数不能仅凭这个比例断言。 |
| Topic 5 的平衡态线性化 | `problem_pack.pdf` PDF p. 8 明确切向中性、法向以速率 2 收缩 | `Section2Draft_.tex` §2.4 从单个奇异值的 `-2` 推断“所有方向收缩”是不完整的。3×3 正交平衡态的 9 个特征值为 `-2`（6 重）及 `0`（3 重）。 |
| Topic 5 的初始谱及稳定步长 | `problem_pack.pdf` PDF p. 8 给出基准 `s=(0.2,1.4,3)`，要求联系初始大奇异值与稳定界；`ODE_IVP_Project_Brief.pdf` PDF p. 1 说明 `hλ` 只是局部冻结 Jacobian 诊断 | `Section2Draft_.tex` §2.4 的“全谱在 `[-26,-2]`、刚性比 13、`h=0.0769/0.1071` 是严格全局上界”均错误。见下方独立计算。 |
| 收敛图 | `lecture1_slides.pdf` PDF p. 11；`lecture2_slides.pdf` PDF p. 18；`Week 2 Supplementary.pdf` PDF p. 18 均强调固定终点、小且稳定的步长、观测斜率是证据而非证明 | `schemes.md` §2.6–2.8 的“减半必为 1/16”“严格收敛至 4.00”应改成渐近预期 `≈1/16`、`p_obs≈4`，并说明前提。 |

## Topic 5 全矩阵谱的核算

令 `X=U diag(s_i) Vᵀ`，在相应正交坐标下作全矩阵线性化：

- 对角方向：`λ_i=1-3s_i²`；
- 每对非对角方向 `i<j`：`λ_ij^±=1-s_i²-s_j²±s_i s_j`。

代入 `s=(0.2,1.4,3)`，得到完整 9 维谱（已用 Python 独立计算）：

`{-26, -14.16, -8.64, -7.44, -5.76, -4.88, -1.28, -0.72, +0.88}`。

`+0.88` 属于最小奇异值从 `0.2` 向 `1` 增长的方向，不应当作数值失稳。
若只描述**初始负实部模态**的衰减率跨度，可报 `26/0.72≈36.1`，并明确
这不是全过程的统一刚性比。`2/26≈0.0769` 与 `2.78529/26≈0.1071`
分别只是初始冻结 Jacobian 对 Euler 和 RK4 的负实轴局部估计；它们既非
全过程严格阈值，也不是精度保证。

在任意正交平衡点 `Q`，`Df(Q)[H]=-2Q sym(QᵀH)`，因此对称法向有 6 个
`-2`，斜对称切向有 3 个 `0`，恰好落实了题目给出的中性/收缩方向。

## 修改优先级

1. 先改 `adaptive.md` §8.1 的“提高一阶”、§7 的稳定性保证、§8.3 的成本。
2. 改 `Section2Draft_.tex` §2.4 的全谱、刚性比及“严格上界”，并补全中性切向方向。
3. 改 `schemes.md` §3.8 的 A-稳定性边界；统一局部缺陷记号，收紧“严格 4.00”等表述。
4. 保留先前审计中 Newton 候选残差、终点裁剪、缺失稳定域图等与课件并不冲突的修正。

详细 GitHub 行号及其他审计项见 `THEORY_AUDIT_2026-09-27.md`。本次仅在本地
修订了审计文档，未更改 GitHub 理论稿。
