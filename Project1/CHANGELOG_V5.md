# v5 修改与复核记录

本文记录 `report/Section2Draft_v5.tex`、中英文代码和运行结果之间的对应关系。理论基线是组员提供的最新 `Section2Draft.tex`／聊天中粘贴的同版正文；项目要求以课程 Problem Pack 的 Topic ⑤ 为准。原始附件没有被改写。

## 一、理论瑕疵怎样修正

| 位置与原问题 | v5 修正 | 对应实现或验证 |
|---|---|---|
| 隐式 Euler 把“把精确终点代入离散方程得到的残差”直接当成实际一步映射误差，两者定义冲突。 | 定义实际隐式根 `w_h`，一步误差为 `y(t_{n+1})−w_h`；另定义精确终点残差 `r=y(t_{n+1})−y(t_n)−hf(t_{n+1},y(t_{n+1}))`。先展开 `r=−h²y''(t_n)/2+O(h³)`，再在选定根存在、局部 Lipschitz 且 `hL<1` 时用 `(1−hL)||ρ||≤||r||` 证明 `ρ=r+O(h³)`。因此隐式 Euler 的一阶结论成立，且没有把该小步条件误写成 A 稳定条件。 | `code/solvers.py`／`code_zh/solvers.py` 真正求解 `F(w)=w−y_n−hf(t_{n+1},w)=0`，并检查 Newton 残差。固定步收敛斜率约 `1.014`。 |
| “足够光滑”没有明确支持文中较强的 Taylor 余项。 | 指定有界邻域上的 `f∈C⁵` 和有限区间上的 `y∈C⁶`，说明 Topic ⑤ 的多项式右端与有限时间解满足该条件；阶数结论本身需要的条件可更弱。 | `code/model.py` 中右端是三次多项式；有限时间 SVD 公式给出验证用精确矩阵。 |
| RK4 的负实轴稳定区间只有结论，缺少排除 `R(−a)=−1` 和端点唯一性的论证。 | 给出 `24R(−a)=(a²−2a)²+8(a−3/2)²+6>0`，再由 `R(−a)−1=a(a³−4a²+12a−24)/24` 及该三次式导数恒正，得到唯一正根 `a*=2.785293563…`，故区间为 `[−a*,0]`。还明确了纯虚轴代入与隐式 Euler 的左半平面稳定性。 | `stability_regions.png` 画三种方法的标量测试稳定域；`frozen_spectrum.png` 将初始完整 9×9 Jacobian 谱叠加在两种显式方法的负实轴界限上。 |
| 步长加倍的“细步”与 Richardson 修正容易混淆。 | 明确估计误差为 `(y_f−y_c)/(2^p−1)`，接受的是 `y_f`，没有用外推后的状态；因此基础方法仍是 `p` 阶。局部估计通过不保证全局精度或非线性稳定。 | 两版 `solvers.py` 的 `solve_adaptive` 一致；报告算法与代码均是一个全步、两个半步、逐分量归一化误差、失败重试。 |
| 初始冻结谱的正特征值容易被误称为数值不稳定；稳定域覆盖容易被误当作非线性全局证明。 | 写出完整初始谱：`−26, −14.16, −8.64, −7.44, −5.76, −4.88, −1.28, −0.72, +0.88`。`+0.88` 是初始小奇异值朝 1 增长的真实动力学；平衡态有 3 个零切向模态与 6 个 `−2` 法向模态。冻结谱只用于局部步长诊断。 | 两版 `model.py` 的解析 Jacobian；`summary.json` 保存两组完整特征值；`stability_sweep.png/.csv` 用非线性步长扫描检验局部预测。 |
| 原算法与代码不一致，报告中也有空图、通用示例和虚构参考文献。 | 数值实现完成后重写阻尼 Newton 与自适应步长伪代码；接入八张真实图片、实测表格和结果讨论；改用可核查的数值 ODE、极分解和 SciPy 文献。 | 报告第 3–4 节、`code/figures/summary.json`、六份 CSV 与两份 README 一一对应。 |

## 二、代码交付

已覆盖原 `code/` 与 `code_zh/` 中的四个源文件；英文版和中文注释版均可独立运行。`model.py` 实现模型、解析 Jacobian、有限时间精确解和诊断；`solvers.py` 实现显式 Euler、经典 RK4、隐式 Euler、固定网格与步长加倍；`experiments.py` 负责所有实验、图表、CSV 与摘要；`run_all.py` 是入口。每个文件的完整职责、命令、参数及每张图的解释见 `README_EN.md` 和 `README_ZH.md`。

本次代码补齐了匹配精度的工作量比较，并修正自适应求解器“最后一次允许的试探恰好成功到达终点，却被误报为超过次数”的边界问题。轨迹图增加离散 Lyapunov 恒等式残差；摘要增加奇异值是否逐次靠近 1、完整初始／平衡态谱。残差以 `max(1, |理论变化率|)` 缩放时称“缩放残差”，不称严格相对误差。

## 三、生成的图与数据

两版分别写入 `code/figures/`、`code_zh/figures/`。八张 PNG 分别是：`convergence.png`（三方法完整矩阵收敛阶、理论斜率和描述性回归带）、`cost_accuracy.png`（多网格实际误差与 RHS 次数曲线，星号标出同精度比较点）、`stability_regions.png`（三个标量稳定域）、`frozen_spectrum.png`（初始完整谱与显式稳定边界）、`stability_sweep.png`（非线性步长扫描）、`trajectory_diagnostics.png`（奇异值、精确能量、正交性、Lyapunov 残差）、`adaptive_steps.png`（接受的自适应步长）、`rank_deficient.png`（秩亏情况下的数值与精确奇异模态）。六份 CSV 保存相应实验的可复查数值；`summary.json` 保存设置和关键结果。每个图的读法和对应 CSV 见双语 README。

按可视化 guide 复查后，收敛图补画拟合中心线，轨迹和秩亏图在图例中标明精确解虚线，并在适用坐标轴上写明无量纲。报告第 885 行把一步映射 Lipschitz 上界的推导关系从 “Equivalently” 更正为 “Consequently”。`report_v1/` 单独保存可编译的 LaTeX 源码、八张报告图片和 PDF；`code/`、`code_zh/`、`report_v1/checklist/` 与双语 README 对应当前实现。

按照提交清单补充 `slides/Topic5_presentation.tex/.pdf` 作为 11 页、约 10 分钟的演示内容初稿。展示批次、讲者姓名和最终排练由小组确认。

## 四、实际运行与证据

在 `Project1` 下执行 `python code/run_all.py`、`python code_zh/run_all.py` 和 `python -m unittest discover -s report_v1/checklist -v`，两版运行成功，摘要一致。Topic ⑤ 原题复核后补入环境梯度流与正交群切向投影的区别，并增加对角初值的独立标量 sanity check；现在 10 项测试通过。显式 Euler、RK4、隐式 Euler 的固定步收敛斜率分别为 `1.010`、`3.927`、`1.014`；独立 Radau 解与完整有限时间 SVD 解在终点的 Frobenius 差为 `1.16×10⁻¹³`。

匹配精度实验采用步数 `(160,17,160)`，三方法的终点误差分别为 `(9.2066,8.8502,9.3194)×10⁻⁴`，最大与最小之比为 `1.053`；RHS 调用为 `(160,68,862)`。这只是 RHS 次数比较，Jacobian、Newton 及线性代数工作分别说明，不能当成运行时间排名。RK4 `h=0.005` 的终点正交性缺陷为 `0.305932824226`，精确有限时间值为 `0.305932824210`，因此不应要求有限终点达到机器零。

## 五、提交前由小组补充

`report/Section2Draft_v5.tex` 的队号、姓名、学号、个人贡献与签名仍需真人填写；AI Transparency Log 目前只记载本次 v5 工作，其他组员若使用了工具须如实补全。本机使用 TeX Live 2022 的 `pdflatex` 完成编译并复跑交叉引用，生成了 27 页的 `report/Section2Draft_v5.pdf`；最终编译日志没有未定义引用、缺失图片或 overfull 警告，也已逐页查看缩略图及关键页排版。今后可从 `Project1/report/` 再运行两次 `pdflatex Section2Draft_v5.tex` 更新 PDF。此本地目录不是 Git 工作树，没有代替你提交或推送到 GitHub。
