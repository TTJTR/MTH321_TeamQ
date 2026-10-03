# 极因子梯度流数值积分的理论基础

> 基于报告 *Numerical Integration of the Polar-Factor Gradient Flow*（MTH321 Project 1, Team Q）第 1–2 章整理。

---

## 1. 问题背景与数学模型

### 1.1 极分解

对任意非奇异矩阵 $X_0 \in \mathbb{R}^{n\times n}$，存在唯一的**极分解**

$$
X_0 = QH,
$$

其中 $Q$ 为正交矩阵，$H$ 为对称正定矩阵。正交因子 $Q$ 在矩阵归一化、矩阵空间上的优化以及数值线性代数中具有重要作用。

### 1.2 极因子梯度流

本报告研究的矩阵微分方程为

$$
\dot X(t) = X(t)\bigl(I_n - X(t)^{\mathsf T}X(t)\bigr),\qquad X(0)=X_0. \tag{1}
$$

该流保持 $X$ 的奇异向量不变，并把全部奇异值驱动到 1，因此当 $t\to\infty$ 时 $X(t)$ 趋于极分解的正交因子。

### 1.3 梯度流（Lyapunov）结构

定义目标泛函

$$
\Phi(X) = \tfrac14\bigl\|X^{\mathsf T}X - I_n\bigr\|_F^2, \tag{2}
$$

其欧氏梯度为 $\nabla\Phi(X) = X(X^{\mathsf T}X - I_n)$，故 (1) 正是 $\Phi$ 的**负梯度流**，且沿精确轨迹有

$$
\frac{d}{dt}\Phi(X(t)) = -\bigl\|X(I_n - X^{\mathsf T}X)\bigr\|_F^2 \le 0. \tag{3}
$$

即 $\Phi$ 是系统的 Lyapunov 泛函，单调递减。这给出了普通误差之外的**结构性诊断量**：数值解的 $\Phi$ 是否单调下降，可检验格式是否尊重问题的几何结构。

> 注：若另有一个约束在正交群上的目标 $g$，其在 $X$（$X^{\mathsf T}X=I_n$）处切空间投影为
> $P_X(G) = G - X\,\mathrm{sym}(X^{\mathsf T}G) = X\,\mathrm{skew}(X^{\mathsf T}G)$。
> 每个正交矩阵都是环境流 (1) 的平衡点。

---

## 2. 精确解：奇异值的 logistic 演化

设 $X_0$ 的 SVD 为 $X_0 = U\Sigma_0 V^{\mathsf T}$。将 $X(t) = U\Sigma(t)V^{\mathsf T}$（奇异向量固定）代入 (1)，每个奇异值独立满足标量 **logistic 型方程**

$$
\dot s_i(t) = s_i(t)\bigl(1 - s_i^2(t)\bigr), \tag{4}
$$

其精确解为

$$
s_i(t) = s_{i,0}\Big/\sqrt{s_{i,0}^2 + \bigl(1-s_{i,0}^2\bigr)e^{-2t}}\,. \tag{5}
$$

性质：

- $0<s_{i,0}<1$：单调上升至 1；$s_{i,0}>1$：单调下降至 1；
- $s_{i,0}=0$ 保持为 0，且标量解互不相交 ⟹ 奇异值次序保持；
- 秩亏初值的极限是**部分等距（partial isometry）**而非正交矩阵。

于是精确有限时刻解

$$
X_{\mathrm{exact}}(t) = U\,\mathrm{diag}\bigl(s_1(t),\dots,s_n(t)\bigr)V^{\mathsf T}, \tag{6}
$$

为数值验证提供了可靠参照（报告中它与独立 Radau 参考解在终端仅相差 $1.16\times10^{-13}$）。

---

## 3. 离散格式

考虑一般初值问题 $\dot y = f(t,y)$，$y(t_0)=y_0$，$f$ 充分光滑且关于 $y$ 局部 Lipschitz。在均匀网格 $t_n = t_0 + nh$ 上，对单步区间积分得精确关系

$$
y(t_{n+1}) - y(t_n) = \int_{t_n}^{t_{n+1}} f(t,y(t))\,dt, \tag{7}
$$

对积分的不同数值近似给出不同格式。矩阵流按列主序向量化 $y=\mathrm{vec}(X)\in\mathbb{R}^{n^2}$ 后与向量形式等价。

### 3.1 显式 Euler（左矩形公式）

$$
y_{n+1} = y_n + h f(t_n, y_n), \qquad
X_{n+1} = X_n + hX_n\bigl(I_n - X_n^{\mathsf T}X_n\bigr). \tag{8}
$$

- 每步 **1 次**右端函数求值，无需解方程组；矩阵流中主要成本为 $O(n^3)$ 的矩阵乘法；
- **条件稳定**，刚性问题下步长限制苛刻。

### 3.2 经典四阶 Runge–Kutta（RK4）

$$
\begin{aligned}
K_1 &= f(X_n), &
K_2 &= f\bigl(X_n + \tfrac h2 K_1\bigr),\\
K_3 &= f\bigl(X_n + \tfrac h2 K_2\bigr), &
K_4 &= f(X_n + hK_3),
\end{aligned}
\qquad
X_{n+1} = X_n + \tfrac h6(K_1 + 2K_2 + 2K_3 + K_4). \tag{9}
$$

Butcher 表：

$$
\begin{array}{c|cccc}
0 & & & & \\
1/2 & 1/2 & & & \\
1/2 & 0 & 1/2 & & \\
1 & 0 & 0 & 1 & \\ \hline
& 1/6 & 1/3 & 1/3 & 1/6
\end{array}
$$

- 每步 **4 次**右端求值；系数矩阵 $A$ 严格下三角 ⟹ 各阶段可顺序显式计算；
- 四阶精度，无需 $f$ 的高阶解析导数。

### 3.3 隐式 Euler 与阻尼 Newton 迭代

右矩形公式给出

$$
X_{n+1} = X_n + hX_{n+1}\bigl(I_n - X_{n+1}^{\mathsf T}X_{n+1}\bigr), \tag{10}
$$

未知量非线性地出现在右端，每步需解非线性方程组。定义残差

$$
F(w) := w - y_n - h f(t_{n+1}, w) = 0. \tag{11}
$$

对 $F$ 在当前迭代点 $w^{(k)}$ 处一阶 Taylor 展开，得 Newton 校正方程

$$
J_F\bigl(w^{(k)}\bigr)\,\delta^{(k)} = -F\bigl(w^{(k)}\bigr),
\qquad
J_F(w) = I_d - h J_f(t_{n+1}, w). \tag{12}
$$

**矩阵流的 Fréchet 导数**：对方向 $H\in\mathbb{R}^{n\times n}$，

$$
Df(X)[H] = H\bigl(I_n - X^{\mathsf T}X\bigr) - X\bigl(H^{\mathsf T}X + X^{\mathsf T}H\bigr). \tag{13}
$$

列主序向量化（$\mathrm{vec}(ABC)=(C^{\mathsf T}\!\otimes A)\mathrm{vec}(B)$，$\mathrm{vec}(H^{\mathsf T})=K_{n,n}\mathrm{vec}(H)$）后，

$$
J_f(X) = I_n\otimes\bigl(I_n - XX^{\mathsf T}\bigr) - \bigl(X^{\mathsf T}\!\otimes X\bigr)K_{n,n} - \bigl(X^{\mathsf T}X\bigr)^{\mathsf T}\!\otimes I_n. \tag{14}
$$

**阻尼 Newton（回溯线搜索）**：为避免初值落在二次吸引域之外导致全步 Newton 发散，取

$$
w^{(k+1)} = w^{(k)} + \alpha\,\delta^{(k)},\qquad \alpha\in(0,1], \tag{15}
$$

仅当候选步使残差严格下降（$\|F_{\mathrm{try}}\|_\infty < \|F\|_\infty$）时接受，否则 $\alpha\leftarrow\alpha/2$（下限 $10^{-4}$）。收敛判据为**尺度感知**阈值

$$
\|F(w)\|_\infty \le \varepsilon_F\bigl(1 + \|w\|_\infty\bigr),\qquad \varepsilon_F = 10^{-12},\ K_{\max}=20. \tag{16}
$$

---

## 4. 相容性与截断误差

### 4.1 局部截断误差的定义

假设 $f$ 满足 Lipschitz 条件（常数 $L$）并足够光滑。任一单步格式写成增量形式

$$
y_{n+1} = y_n + h\Phi(t_n, y_n, h). \tag{17}
$$

在**局部化假设** $y_n = y(t_n)$ 下，单步局部误差与局部截断误差（LTE）为

$$
\rho_{n+1} := y(t_{n+1}) - \bigl[y(t_n) + h\Phi(t_n, y(t_n), h)\bigr],
\qquad
\tau_{n+1} := \frac{\rho_{n+1}}{h}. \tag{18}
$$

若 $\|\tau_{n+1}\| = O(h^p)$（等价于 $\|\rho_{n+1}\| = O(h^{p+1})$），称格式 **$p$ 阶相容**。

### 4.2 三种格式的 LTE 推导

**显式 Euler（$p=1$）**：对精确解作 Taylor 展开

$$
y(t_{n+1}) = y(t_n) + h\dot y(t_n) + \tfrac{h^2}{2}\ddot y(t_n) + O(h^3), \tag{19}
$$

减去数值增量后零阶、一阶项精确相消：

$$
\rho^{\mathrm{EE}}_{n+1} = \tfrac{h^2}{2}\ddot y(t_n) + O(h^3)
\;\Longrightarrow\;
\tau^{\mathrm{EE}}_{n+1} = \tfrac{h}{2}\ddot y(t_n) + O(h^2). \tag{20}
$$

**隐式 Euler（$p=1$）**：设 $y_* := y(t_{n+1})$，$w_h$ 为隐式方程之根。定义精确端点残差

$$
r^{\mathrm{IE}}_{n+1} := y_* - y(t_n) - h\dot y(t_{n+1}) = -\tfrac{h^2}{2}\ddot y(t_n) + O(h^3). \tag{21}
$$

利用 $F(w_h)=0$ 得恒等式 $r^{\mathrm{IE}}_{n+1} = \rho^{\mathrm{IE}}_{n+1} - h\bigl[f(t_{n+1},y_*) - f(t_{n+1},w_h)\bigr]$；当 $hL<1$ 时由 Lipschitz 条件

$$
(1-hL)\,\|\rho^{\mathrm{IE}}_{n+1}\| \le \|r^{\mathrm{IE}}_{n+1}\|
\;\Longrightarrow\;
\rho^{\mathrm{IE}}_{n+1} = -\tfrac{h^2}{2}\ddot y(t_n) + O(h^3). \tag{22}
$$

**RK4（$p=4$）**：将四个阶段斜率按基本微分展开并与精确 Taylor 级数比对，四阶以内全部阶条件成立（$\sum b_i = 1$，$\sum b_ic_i = 1/2$，…，$\sum b_ia_{ij}a_{jk}c_k = 1/24$），故

$$
\rho^{\mathrm{RK4}}_{n+1} = \psi(t_n)h^5 + O(h^6),\qquad
\tau^{\mathrm{RK4}}_{n+1} = \psi(t_n)h^4 + O(h^5), \tag{23}
$$

其中 $\psi$ 为由五阶基本微分构成的主误差函数。

### 4.3 自适应步长：步长加倍（Richardson）误差估计

设基格式阶为 $p$。从同一接受状态出发：

- **粗解** $y_c$：一整步 $h$，局部误差 $\psi h^{p+1}$；
- **细解** $y_f$：两个半步 $h/2$，误差线性叠加为 $2\psi(h/2)^{p+1} = \psi h^{p+1}/2^p$。

两式相减消去未知精确解，得可计算的局部误差估计

$$
\hat e_n \approx \frac{y_f - y_c}{2^p - 1}
\quad\Longrightarrow\quad
\begin{cases}
p=1 \text{（两种 Euler）}: & \hat e_n \approx y_f - y_c,\\[2pt]
p=4 \text{（RK4）}: & \hat e_n \approx (y_f - y_c)/15.
\end{cases} \tag{24}
$$

### 4.4 误差归一化与步长控制器

分量容差向量与归一化误差比：

$$
s_i = \mathrm{atol} + \mathrm{rtol}\max\bigl(|y_{n,i}|, |y_{f,i}|\bigr),
\qquad
E := \max_i \Bigl|\frac{\hat e_{n,i}}{s_i}\Bigr|. \tag{25}
$$

- $E \le 1$：**接受**，以细解 $y_f$ 推进（保持基格式阶 $p$，非 Richardson 校正解）；
- $E > 1$：**拒绝**，状态不变，缩小步长重试。

由渐近关系 $E(h)\propto h^{p+1}$，令下一步目标 $E\approx 1$，得步长更新

$$
h_{\mathrm{new}} = h\cdot \min\Bigl(r_{\max},\, \max\bigl(r_{\min},\, S\,E^{-\frac{1}{p+1}}\bigr)\Bigr), \tag{26}
$$

典型参数 $S=0.9$，$r_{\min}=0.2$，$r_{\max}=2.0$（安全因子 + 增长/收缩限制器，防止步长振荡）。

---

## 5. 稳定性分析

### 5.1 Dahlquist 测试方程与放大因子

对测试方程 $\dot y = \lambda y$（$\lambda\in\mathbb{C}$，$\mathrm{Re}\,\lambda<0$），记 $z := h\lambda$。单步格式给出几何递推 $y_{n+1} = R(z)y_n$，绝对稳定条件为

$$
|R(z)| \le 1,\qquad
\mathcal{S} := \{z\in\mathbb{C} : |R(z)|\le 1\}. \tag{27}
$$

### 5.2 三种格式的稳定域

**显式 Euler**：

$$
R_{\mathrm{EE}}(z) = 1 + z
\;\Longrightarrow\;
|1+z|\le 1 \iff (x+1)^2 + y^2 \le 1. \tag{28}
$$

- 稳定域为以 $(-1,0)$ 为圆心的单位闭圆盘；负实轴上 $z\in[-2,0]$，即经典限制 $h \le 2/|\lambda|$；
- 虚轴上 $|R_{\mathrm{EE}}(iy)|^2 = 1+y^2 > 1$（$y\ne0$）：对纯振荡系统**无条件不稳定**。

**RK4**：阶段递推合成 $e^z$ 的截断 Taylor 多项式

$$
R_{\mathrm{RK4}}(z) = 1 + z + \frac{z^2}{2!} + \frac{z^3}{3!} + \frac{z^4}{4!}. \tag{29}
$$

- 负实轴：可证 $24R_{\mathrm{RK4}}(-a) = (a^2-2a)^2 + 8(a-\tfrac32)^2 + 6 > 0$，再由 $q(a)=a^3-4a^2+12a-24$ 单调且有唯一正根 $a^* \approx 2.78529$，得 $\mathcal{S}_{\mathrm{RK4}}\cap\mathbb{R} = [-2.78529,\,0]$；
- 虚轴：$|R_{\mathrm{RK4}}(iy)|^2 = 1 + \dfrac{y^6(y^2-8)}{576}$，故稳定段为 $|y| \le 2\sqrt{2}$。

**隐式 Euler**：

$$
R_{\mathrm{IE}}(z) = \frac{1}{1-z}
\;\Longrightarrow\;
|R_{\mathrm{IE}}(z)|\le 1 \iff |1-z|\ge 1 \iff (x-1)^2 + y^2 \ge 1. \tag{30}
$$

稳定域是以 $(+1,0)$ 为圆心的**单位开圆盘的外部**，包含整个闭左半平面。

### 5.3 A-稳定与 L-稳定

- **A-稳定**：$\mathbb{C}^- = \{z : \mathrm{Re}\,z\le0\} \subseteq \mathcal{S}$。对隐式 Euler，$x\le0$ 时 $|1-z|^2 = 1 - 2x + x^2 + y^2 \ge 1$ 恒成立 ⟹ 隐式 Euler 是 A-稳定的；
- **L-稳定**：A-稳定且 $\lim_{|z|\to\infty}|R(z)| = 0$。$\lim_{|z|\to\infty}|1/(1-z)| = 0$ ⟹ 隐式 Euler 是 L-稳定的，对刚性瞬态有强阻尼；
- 显式 Euler 与 RK4 的稳定函数为多项式，$|z|\to\infty$ 时发散，不可能 A-稳定。

### 5.4 问题特定的线性化谱（Topic 5）

写 $X = U\Sigma V^{\mathsf T}$，扰动方向 $H = UKV^{\mathsf T}$，变换后的线性化算子为

$$
\mathcal{L}_\Sigma[K] = K(I_n - \Sigma^2) - \Sigma(K^{\mathsf T}\Sigma + \Sigma K). \tag{31}
$$

- **对角方向**：$\lambda_{ii} = 1 - 3s_i^2$；
- **非对角对 $(i<j)$**：对称扰动 $\lambda^{\mathrm{sym}}_{ij} = 1 - s_i^2 - s_j^2 - s_is_j$；反对称扰动 $\lambda^{\mathrm{skew}}_{ij} = 1 - s_i^2 - s_j^2 + s_is_j$；
- 在正交平衡点（$s_i=1$）：$\lambda^{\mathrm{sym}}_{ij} = -2$（法向收缩，维数 $n(n+1)/2$），$\lambda^{\mathrm{skew}}_{ij} = 0$（沿正交平衡流形的**中性切向**，维数 $n(n-1)/2$）。

基准算例 $X_0 = U\,\mathrm{diag}(0.2, 1.4, 3.0)\,V^{\mathsf T}$ 的冻结 Jacobian 谱：

$$
\sigma(J_f(X_0)) = \{0.88,\ -0.72,\ -1.28,\ -4.88,\ -5.76,\ -7.44,\ -8.64,\ -14.16,\ -26.0\}. \tag{32}
$$

其中 $+0.88$ 是小奇异值 $s_1=0.2$ 向 1 增长的**物理模态**（非数值不稳定）；最快收缩模态 $-26$ 与最慢负模态 $-0.72$ 之比约 36，呈现**多尺度**特征。

由此得显式格式的局部冻结谱步长估计：

$$
h^{\mathrm{EE}}_{\mathrm{crit}} = \frac{2}{26.0} \approx 0.0769,
\qquad
h^{\mathrm{RK4}}_{\mathrm{crit}} = \frac{2.78529}{26.0} \approx 0.1071. \tag{33}
$$

> **重要声明**：冻结 Jacobian 谱分析只是**局部诊断**，不是全局非线性稳定性证明——Jacobian 沿轨迹连续变化，$|R(h\lambda_j)|\le1$ 不能保证非线性收敛，必须通过步长扫描与扰动实验检验。

---

## 6. 全局收敛性：离散 Grönwall 引理

### 6.1 误差递推

真解满足带扰动关系 $y(t_{n+1}) = y(t_n) + h\Phi(t_n, y(t_n), h) + h\tau_{n+1}$。设增量函数 $\Phi$ 关于状态一致 Lipschitz（常数 $\Lambda$，对充分小 $h$ 一致；对隐式 Euler 还需根存在且 $\|(I_d - hJ_f)^{-1}\| \le M_J$ 一致有界）。全局误差 $e_n := y(t_n) - y_n$ 满足

$$
\|e_{n+1}\| \le (1 + h\Lambda)\|e_n\| + h\|\tau_{n+1}\|. \tag{34}
$$

### 6.2 离散 Grönwall 界

记 $\tau_{\max}(h) := \max_k\|\tau_k\|$，由 $e_0 = 0$ 递推展开并求几何级数，利用 $1+x \le e^x$：

$$
\|e_n\| \le h\,\tau_{\max}(h)\sum_{j=0}^{n-1}(1+h\Lambda)^j
= \tau_{\max}(h)\,\frac{(1+h\Lambda)^n - 1}{\Lambda}
\le \frac{e^{\Lambda(T-t_0)} - 1}{\Lambda}\,\tau_{\max}(h). \tag{35}
$$

### 6.3 全局收敛阶

- 两种 Euler（$\tau = O(h)$）：$\|e_N\| = O(h)$；
- RK4（$\tau = O(h^4)$）：$\|e_N\| = O(h^4)$。

**阶的来源**：单步局部缺陷为 $O(h^{p+1})$，但在区间 $[t_0,T]$ 上累积 $N = O(h^{-1})$ 步，故全局阶为 $O(h^p)$——相容性 + 一致 Lipschitz 稳定性 ⟹ 收敛（单步方法无需多步法的根条件）。

> 隐式 Euler 还要求 Newton 代数误差不超过时间离散误差量级（每步残差 $O(h^2)$ 即充分）；报告中固定容差 $10^{-12}$，用 $10^{-14}$ 复算终端解变化不超过约 $1.14\times10^{-8}$，远小于离散误差，故不影响收敛实验。

### 6.4 log–log 实验验证

终端 Frobenius 误差 $E_h(T) = \|X_h(T) - X_{\mathrm{exact}}(T)\|_F \approx Ch^p$，取对数得

$$
\ln E_h \approx p\ln h + \ln C, \tag{36}
$$

即 log–log 图上斜率即为收敛阶 $p$。相邻步长的实测阶

$$
p_{\mathrm{obs}}(h) = \frac{\log\bigl(E_h(T)/E_{h/2}(T)\bigr)}{\log 2}. \tag{37}
$$

报告实测斜率：显式 Euler $\approx 1.010$，RK4 $\approx 3.927$，隐式 Euler $\approx 1.014$，与理论阶 1、4、1 一致。

---

## 7. 理论要点小结

| 性质 | 显式 Euler | RK4 | 隐式 Euler |
|---|---|---|---|
| 局部截断误差 | $O(h^2)$ | $O(h^5)$ | $O(h^2)$ |
| 全局收敛阶 | 1 | 4 | 1 |
| 每步 RHS 求值 | 1 | 4 | 每次 Newton 迭代 1 次 + 线性求解 |
| 稳定域（负实轴） | $[-2,\,0]$ | $[-2.78529,\,0]$ | 整个左半平面 |
| A-稳定 / L-稳定 | 否 / 否 | 否 / 否 | 是 / 是 |
| 本问题临界步长（估计） | $\approx 0.0769$ | $\approx 0.1071$ | 无（线性意义下） |

**核心逻辑链**：
梯度流结构（Lyapunov 递减）+ SVD 精确解 ⟹ 可靠参照；
相容性（LTE 阶）+ Lipschitz 稳定性（离散 Grönwall）⟹ 全局收敛阶；
绝对稳定性（稳定域、A/L-稳定 + 冻结谱局部诊断）⟹ 有限步长下格式的可行性与刚性下的取舍——显式格式受瞬态快模态限制，隐式 Euler 以非线性求解为代价换取大步长鲁棒性，RK4 在同等终端精度下以最少 RHS 求值次数取得精度与效率的平衡。
