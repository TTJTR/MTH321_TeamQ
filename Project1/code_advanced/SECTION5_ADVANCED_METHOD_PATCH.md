# Section 5「方法进阶」参考补丁

> 交接用途：这是一份**代码、图片、数据及理论说明补丁**，供负责报告的同学写下一版的 Section 5。它不是报告正文，也不是 LaTeX 模板。当前 `report_v3/` 原文、原代码与原输出均不改动。

## 1. 插入位置与边界

当前报告顺序是 Section 1 Background、Section 2 Discretisation and Analysis、Section 3 Implementation、Section 4 Numerical Experiments、Section 5 Conclusions。下一版若采用本扩展，在 Section 4 之后插入一个独立的 **Section 5: Advanced Method — Fourth-Order Gauss Implicit Runge–Kutta**；原 Conclusions 自动成为 **Section 6**。章节编号应交由 LaTeX 自动生成，原 `section5.tex` 的结论正文目前无需重写。

原 Sections 2–4 的三方法主线继续保持原口径：显式 Euler、显式 RK4、隐式 Euler 是作业的基础方法。本补丁的方法是**额外的高级方法对照**；它没有实现自适应 Gauss 步长，也没有提出新的非标准收敛定理。报告同学将来可以自行决定是否在摘要、结论和附录补一句扩展说明；本补丁不修改这些原文。需注意旧摘要写“三种方法”，新 Section 应明确“前三种是基础方法，Gauss IRK4 是独立扩展”，避免读者误以为旧表格和旧自适应实验已经包含第四种方法。

## 2. 方法来源：引用哪本书、哪一节

这里的“隐式 RK4”是**两阶段、四阶 Gauss–Legendre 隐式 Runge–Kutta 法**（简称 Gauss IRK4）。“四阶”指精度阶数；它不是四阶段的经典显式 RK4，也不是自行发明的方法。

主要文献：J. C. Butcher, *Numerical Methods for Ordinary Differential Equations*, 3rd ed., Wiley, 2016，**Chapter 3, §34.2 “Methods based on Gaussian quadrature,” pp. 228–232**，用于 Gauss 方法与两阶段系数；**§35.3 “A-stability of Gauss and related methods,” p. 252 起**，用于稳定性；**§36.0 “Implementation of implicit Runge–Kutta methods,” p. 272 起**，用于求解实现背景。[Wiley 第 3 章](https://onlinelibrary.wiley.com/doi/10.1002/9781119121534.ch3)、[第三版目录及页码](https://toc.library.ethz.ch/objects/pdf03/z01_978-1-119-12150-3_01.pdf)、[Butcher 本人的两阶段方法系数表](https://www.math.auckland.ac.nz/~butcher/ODE-book-2008/Tutorials/IRK.pdf)。

Griffiths 与 Higham, *Numerical Methods for Ordinary Differential Equations: Initial Value Problems* (Springer, 2010) 的 Chapters 9–11 可作为隐式方程、RK 阶条件和绝对稳定性的背景，但**本次具体 Gauss 系数的主出处是 Butcher**。[Springer 书籍目录](https://link.springer.com/book/10.1007/978-0-85729-148-6)。

## 3. Section 5 的理论内容应如何写

### 3.1 方法如何作用于本题

沿用原报告的矩阵 ODE 和列优先向量化，令 `y=vec(X)∈R⁹`、`f(y)=vec[X(I−XᵀX)]`。两阶段节点为 `c₁=1/2−√3/6`、`c₂=1/2+√3/6`，权重均为 `1/2`，系数矩阵为

```text
A = [ 1/4              1/4 − √3/6 ]
    [ 1/4 + √3/6       1/4        ]
```

每一步同时求解 `Yᵢ = yₙ + h Σⱼ aᵢⱼ f(Yⱼ)`（`i=1,2`），再用 `yₙ₊₁ = yₙ + h[f(Y₁)+f(Y₂)]/2` 更新。两阶段互相依赖，不能按两个独立的 9 维方程依次求解。

### 3.2 隐式阶段如何求解

定义耦合残差 `Fᵢ(Y₁,Y₂)=Yᵢ−yₙ−h Σⱼ aᵢⱼ f(Yⱼ)`。其 `(i,j)` 分块 Jacobian 是 `δᵢⱼ I₉ − h aᵢⱼ J_f(Yⱼ)`，因此每次 Newton 更新求解一个 **18×18** 线性系统。代码用预测值 `Yᵢ⁽⁰⁾=yₙ+cᵢh f(yₙ)` 起步，并采用阻尼 Newton；只有完整阶段残差有限且下降时才接受试探修正。若达到迭代上限或线搜索失败，固定步长求解器报告失败，不会悄悄改步长。

停止条件是 `‖F‖∞ ≤ 10⁻¹²(1+‖Y‖∞)`。这个 `10⁻¹²` 是**阶段方程的残差阈值**，不是全局数值解精度。报告中必须把两者区分。

### 3.3 为什么是四阶，以及何时可接上原报告的收敛论证

两阶段 Gauss 配点法的经典阶数定理给 `p=2s=4`。本实现的系数也逐项满足原报告列出的全部八个四阶 RK 条件。因此**精确求出阶段根**时，单步缺陷是 `O(h⁵)`，原报告定义的每单位步长 LTE 是 `O(h⁴)`。本题的 `f(X)=X(I−XᵀX)` 是多项式，在所考虑的有限时间有界邻域上具备所需光滑性。

要把它接入原 Section 2 的全局误差递推，还需明确阶段根的局部条件：设 `f` 在包含相关阶段状态的有界邻域内 Lipschitz，常数为 `L`；当步长足够小并满足 `h‖A‖∞L<1` 时，所选阶段方程在该邻域有局部唯一根。阶段根对起始状态的敏感度由 `1/(1−h‖A‖∞L)` 控制，故 Gauss 一步增量具有对充分小 `h` 统一的局部 Lipschitz 界。沿用原报告的离散 Grönwall 论证，可得固定有限时间上的全局 `O(h⁴)`，前提是精确与数值轨道留在这个邻域内。**这属于经典理论在本题上的应用，不是新的收敛理论。**

实际计算得到的是近似阶段根。若阶段残差为 `ε(h)` 且上述局部逆界成立，阶段误差为 `O(ε)`，一步更新多出 `O(hε)`，固定时间内累积为 `O(ε)`。因此要作为严格的 `h→0` 四阶算法论断，可令阶段残差随步长满足 `ε(h)=O(h⁴)`。代码采用固定 `10⁻¹²`，所以报告只能说**当前有限网格上的结果通过了容差敏感性核对**，不能声称无限细网格仍自动保持四阶。原隐式 Euler 的“终点方程残差”与这里的“阶段残差”不是同一种残差，不应直接搬用它的尺度条件。

### 3.4 A 稳定与非 L 稳定：两者都要写

对标量测试方程 `y′=λy`、`z=hλ`，新方法的放大函数为

```text
R_G(z) = (1 + z/2 + z²/12) / (1 − z/2 + z²/12).
```

令分子、分母分别为 `N(z)`、`D(z)`，可直接计算

```text
|D(z)|² − |N(z)|² = −2 Re(z) [1 + |z|²/12] ≥ 0    当 Re(z)≤0。
```

分母零点 `3±i√3` 都在右半平面，因此左半平面内 `|R_G(z)|≤1`，即 **A 稳定**。另一方面，沿负实轴 `z→−∞` 时 `R_G(z)→1`，所以它**不是 L 稳定**：在非常大的负 `hλ` 下，快模态不一定被强烈消除。这一点尤其不能与隐式 Euler 的 L 稳定性混同。

这些是**标量线性测试方程**的性质。将本题初始 Jacobian 的最快负特征值 `−26` 代入，在 `h=0.08` 时 `z=−2.08`，Gauss 放大因子约为 `0.1335`。本题初始还有一个 `+0.88` 的物理增长模态；A 稳定不要求抑制正实轴模态。初始谱随非线性轨道改变，因此一次冻结谱计算也不是全程稳定性证明。

### 3.5 数值证据与结论应怎样限定

在原题的 `X₀`、区间 `[0,2]` 上，仍以**有限时间 SVD 精确矩阵**计算终点 Frobenius 误差。Gauss 在 `N=64,128,256` 三个细网格上的拟合阶为 **3.9674**，与四阶预期一致。原三方法在同一新脚本中的拟合阶约为 Euler `1.0101`、显式 RK4 `3.9274`、隐式 Euler `1.0137`。

新成本图给出了几乎等误差的固定步长对照：显式 RK4 用 `N=75`，终点误差 `5.09443×10⁻⁸`、**300 次 RHS**；Gauss IRK4 用 `N=64`，终点误差 `5.07898×10⁻⁸`、**720 次 RHS、264 次 Jacobian、132 次 Newton**。两误差相差约 `0.3%`。因此，在这个 `3×3` 基准和该误差水平下，Gauss 并未节省 RHS 调用；横轴也没有计入 Jacobian 组装、18×18 线性求解和 Python 开销，不能把它解释成真实运行时间的量化比较。

在共同 `h=0.1` 网格上，四种方法的**已采样** Lyapunov 能量逐步下降。这是该实验的观察，不能写成“Gauss 对任意步长保持能量单调”。固定阈值 `10⁻¹²` 收紧为 `10⁻¹⁴` 后，Gauss 在 `N=64,128,256` 的终点变化约为 `4.44×10⁻¹⁶`、`1.50×10⁻¹³`、`3.47×10⁻¹⁴`，均远小于各自的时间离散误差。

## 4. 代码、图片和数据补丁

原 `code/`、`code_zh/`、原八张报告图与原数据保留。新增部分独立放在以下位置：

| 路径 | 内容及用途 |
|---|---|
| `code_advanced/gauss_irk4.py` | Gauss 系数、18 维耦合阶段阻尼 Newton、固定步长驱动、工作量计数、标量稳定函数 |
| `code_advanced/run_comparison.py` | 用相同模型与有限时间解析解比较四方法；只写入新子目录 |
| `code_advanced/test_gauss_irk4.py` | 检验四阶条件、标量稳定性、矩阵四阶、Newton 失败、容差敏感性、能量与秩亏情形 |
| `code_advanced/README.md` | 英中双语文件说明与运行命令 |
| `figures/advanced_irk4/convergence_comparison.png` | 四方法的终点矩阵误差与步长；看拟合阶 |
| `figures/advanced_irk4/cost_comparison.png` | 终点误差与 RHS 次数；星号是 `N=75` RK4 与 `N=64` Gauss 的约 0.3% 等误差点 |
| `figures/advanced_irk4/stability_comparison.png` | 四方法负实轴放大因子；虚线标出 `−26×0.08`，展示 Gauss 的非 L 稳定行为 |
| `figures/advanced_irk4/energy_comparison.png` | 共同 `h=0.1` 时四方法的离散能量轨迹 |
| `data/advanced_irk4/convergence_cost.csv` | 网格、步长、误差、RHS/Jacobian/Newton 计数和等误差对照标记 |
| `data/advanced_irk4/energy_trajectories.csv` | 能量图背后的逐时刻数据 |
| `data/advanced_irk4/summary.json` | 拟合阶、放大因子、等误差对照点与成本说明 |

从项目根目录运行：

```text
python -B code_advanced/run_comparison.py
python -B -m unittest discover -s code_advanced -p "test_*.py" -v
python -B -m unittest discover -s test -v
```

报告同学若决定在新版本中使用图片，应把四图和配套数据复制到**新报告版本自身**的 `figures/advanced_irk4/` 与 `data/advanced_irk4/`，或明确设置图片路径；旧版 `report_v3/` 的快照不要覆盖。图、CSV 和文字数字必须来自同一次脚本运行。

### LaTeX 应引用哪个文件夹的图片

**本补丁在 GitHub 上的图片源目录是 `Project1/figures/advanced_irk4/`。** Section 5 只引用这个目录的四张 PNG，不引用 `Project1/report_v3/figures/` 里的旧三方法图片，也不引用 `Project1/code_advanced/` 里的文件作为图片。

推荐由报告同学把这四张图复制到新报告版本的 `Project1/report_v4/figures/advanced_irk4/`（若版本另有名称，替换 `report_v4`），保持报告快照自包含。由于现有报告使用 `\graphicspath{{figures/}}`，新 Section 的图片名分别写成：

```text
advanced_irk4/convergence_comparison.png
advanced_irk4/cost_comparison.png
advanced_irk4/stability_comparison.png
advanced_irk4/energy_comparison.png
```

即例如 `\includegraphics{advanced_irk4/convergence_comparison.png}`。若不复制、直接从 `report_v4/` 编译并引用项目级图片，则相对路径是 `../figures/advanced_irk4/convergence_comparison.png`（其余三图同理）；这要求编译工作目录与上述相对位置一致。**复制到新版报告自身的 `figures/` 更稳妥。** 同理，图后面的数据源是 `Project1/data/advanced_irk4/`，建议复制到新版报告的 `data/advanced_irk4/`。

## 5. 交接时要避免的五种误写

1. 把 Gauss IRK4 写成“四阶段隐式 RK4”或本组原创算法。它是**两阶段四阶**经典 Gauss 配点法。
2. 把 A 稳定写成 L 稳定，或把标量稳定性当作非线性矩阵流的全局证明。
3. 把固定 `10⁻¹²` 阶段残差说成全局解误差上界；将原隐式 Euler 的终点残差条件原样套到耦合阶段残差。
4. 把三基础方法的自适应结果、旧成本表或旧附录数据说成已经包含 Gauss；新增实验只做**固定步长**。
5. 因为新增 Section 5 就声称完成了另一条三星要求“develop convergence theory for non-standard methods or problems”。这里使用的是经典 Gauss 方法及标准收敛论证。

## 6. 当前完成状态

- 新方法测试 **6/6 通过**，原三方法测试 **14/14 通过**；新脚本可重生四张 PNG、两份 CSV 与一个 JSON。
- `report_v3/` 尚未加入 Section 5，原 Conclusions 尚未在实际 PDF 中重编号；本补丁只规定下一版的插入位置。
- 正式新版报告完成后，仍需检查目录、图路径、引用、数据快照及编译后的 PDF；本补丁不代替报告编译验收。
