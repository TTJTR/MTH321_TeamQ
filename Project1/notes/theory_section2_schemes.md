D. 知识点讲解：三大方法的完整推导

1. 显式欧拉法 (Explicit Euler)

1.1 推导目标

推导显式欧拉格式 $y_{n+1} = y_n + h f(t_n, y_n)$，证明其局部缺陷为 $O(h^2)$，全局收敛阶数为 $O(h)$。

1.2 假设与适用条件

- 设连续模型 $\dot{y} = f(t, y), y(t_0) = y_0$，右端项 $f(t, y)$ 关于 $y$ 满足 **Lipschitz 连续条件** $\|f(t, u) - f(t, v)\| \le L \|u - v\|$ 。
- 解函数 $y(t) \in C^2[t_0, T]$，即二次连续可导 。

1.3 符号定义

- $t_n = t_0 + n h$ 为离散时间点，$N = T/h$ 为总步数。
- $y(t_n)$ 表示 $t_n$ 时刻的连续**精确解**；$y_n$ 表示离散**数值近似解** 。
- $e_n = y_n - y(t_n)$ 为 $t_n$ 时刻的**全局误差 (Global Error)** 。

1.4 从第一原理出发

连续 ODE 在区间 $[t_n, t_{n+1}]$ 上的精确积分形式为： $$y(t_{n+1}) = y(t_n) + \int_{t_n}^{t_{n+1}} f(t, y(t)) \mathrm{d}t$$ 

- **途径 A（数值积分近似）**：采用**左端点矩形法则**逼近积分项：$\int_{t_n}^{t_{n+1}} f(t, y(t)) \mathrm{d}t \approx h f(t_n, y(t_n))$ 。
- **途径 B（泰勒展开）**：将精确解 $y(t_{n+1}) = y(t_n + h)$ 在 $t_n$ 处进行带拉格朗日余项的泰勒展开 ： $$y(t_{n+1}) = y(t_n) + h y'(t_n) + \frac{1}{2} h^2 y''(\xi_n) = y(t_n) + h f(t_n, y(t_n)) + \frac{1}{2} h^2 y''(\xi_n), \quad \xi_n \in (t_n, t_{n+1})$$

1.5 连续模型到离散格式

忽略高阶余项 $\frac{1}{2} h^2 y''(\xi_n)$，将精确状态 $y(t_n)$ 替换为数值状态 $y_n$，得到离散递推格式 ： $$\mathbf{y_{n+1} = y_n + h f(t_n, y_n)}$$

1.6 局部截断误差、全局误差与阶数

- **局部单步缺陷 (One-step Local Defect** $d_{n+1}$**)**：假设起点完全精确（$y_n = y(t_n)$），一步产生的误差为： $$d_{n+1} = y(t_{n+1}) - \left[ y(t_n) + h f(t_n, y(t_n)) \right] = \frac{1}{2} h^2 y''(\xi_n) \implies \|d_{n+1}\| \le C h^2 = O(h^2)$$ 归一化局部截断误差 (LTE) 为 $\tau_{n+1} = \frac{d_{n+1}}{h} = O(h)$ 。
- **全局误差递推与 Gronwall 累积 (Global Error)**： 将数值递推式 $y_{n+1} = y_n + h f(t_n, y_n)$ 与精确泰勒展开式 $y(t_{n+1}) = y(t_n) + h f(t_n, y(t_n)) + d_{n+1}$ 相减 ： $$e_{n+1} = e_n + h \left[ f(t_n, y_n) - f(t_n, y(t_n)) \right] - d_{n+1}$$ 利用 Lipschitz 条件取范数 ： $$\|e_{n+1}\| \le (1 + h L) \|e_n\| + \|d_{n+1}\| \le (1 + h L) \|e_n\| + C h^2$$ 从初始无误差 $e_0 = 0$ 展开递推序列： $$\|e_N\| \le C h^2 \sum_{j=0}^{N-1} (1 + h L)^j = C h^2 \frac{(1 + h L)^N - 1}{h L}$$ 利用不等式 $(1 + h L)^N \le e^{N h L} = e^{L T}$（其中 $N h = T$）： $$\|e_N\| \le \frac{C}{L} \left( e^{L T} - 1 \right) h = O(h)$$ **结论**：每步注入 $O(h^2)$ 的局部误差，经 $N = T/h$ 步放大大约 $1/h$ 倍后，**全局收敛阶数为一阶** $p=1$ 。

1.7 稳定性分析

带入线性测试方程 $\dot{y} = \lambda y$ ($\lambda \in \mathbb{C}$)，设 $z = h \lambda$： $$y_{n+1} = y_n + h \lambda y_n = (1 + z) y_n \implies R(z) = 1 + z$$ 绝对稳定性条件为 $|R(z)| \le 1 \iff |z + 1| \le 1$，即复平面上**以** $-1$ **为圆心、半径为** $1$ **的闭圆盘** 。对于实负特征值，步长严格受限于 $h \le \frac{2}{|\lambda|}$。

1.8 数值含义与可验证预测

单步仅需 1 次右端项评估，简单极快，但在刚性方程（如 Robertson 或大 $\mu$ Van der Pol）上极易因越出稳定圆盘而发生数值发散（Blow-up）。在对数-对数图（Log-log error plot）上测得的拟合斜率 $p_{\text{obs}} \approx 1.00$。

---

2. 四阶龙格-库塔法 (Classic RK4)

2.1 推导目标

推导四阶 Runge-Kutta 离散更新格式，阐明其四阶段斜率采样的代数设计，并证明其全局误差阶数为 $O(h^4)$ 。

2.2 假设与适用条件

右端项 $f(t, y)$ 至少具有 $C^4$ 连续偏导数，允许进行高阶多元泰勒展开 。

2.3 符号定义与 Butcher 表格 (Butcher Tableau)

显式 $s$ 阶段 RK 方法的一般形式为 $y_{n+1} = y_n + h \sum_{i=1}^s b_i k_i$，其中 $k_i = f\left(t_n + c_i h, y_n + h \sum_{j=1}^{i-1} a_{ij} k_j\right)$ 。 经典 RK4 的 Butcher 表格结构为 ]： 
$$
\begin{array}{c|cccc}
0 & & & & \\
1/2 & 1/2 & & & \\
1/2 & 0 & 1/2 & & \\
1 & 0 & 0 & 1 & \\
\hline
& 1/6 & 1/3 & 1/3 & 1/6
\end{array}
$$

2.4 从第一原理出发

RK4 是对 Simpson 积分公式 $\int_{t_n}^{t_{n+1}} f(t, y(t)) \mathrm{d}t \approx \frac{h}{6} \left[ f_n + 4 f_{n+1/2} + f_{n+1} \right]$ 的高阶代数推广 。为了避免求解高阶导数 $y'', y'''$，它在单步内巧妙地检测四个位置的斜率 ：

1. $k_1$**（起点斜率）**：$k_1 = f(t_n, y_n)$ 
2. $k_2$**（中点试探斜率 1）**：用 $k_1$ 跨越半步：$k_2 = f\left(t_n + \frac{h}{2}, y_n + \frac{h}{2} k_1\right)$ 
3. $k_3$**（中点试探斜率 2）**：用更准的 $k_2$ 重新跨越半步：$k_3 = f\left(t_n + \frac{h}{2}, y_n + \frac{h}{2} k_2\right)$ 
4. $k_4$**（终点试探斜率）**：用 $k_3$ 跨越一步：$k_4 = f(t_n + h, y_n + h k_3)$ 

2.5 连续模型到离散格式

对四个斜率进行加权平均加总： $$\mathbf{y_{n+1} = y_n + \frac{h}{6} \left( k_1 + 2 k_2 + 2 k_3 + k_4 \right)}$$

2.6 局部截断误差与全局阶数匹配

通过有根树（Rooted Trees / B-series）匹配多元泰勒展开：

- 精确解泰勒展开至 $h^4$ 项包含 8 个代数微分树条件（Order conditions）。
- RK4 的系数 $a_{ij}, b_i, c_i$ 恰好精确消去了展式中直到 $h^4$ 的所有误差项，使得单步局部截断误差满足： $$\delta_{n+1} = y(t_{n+1}) - y_{n+1} = O(h^5)$$
- 经过 $N = T/h$ 步累积后，**全局收敛误差为** $E(h) = O(h^4)$ 。步长减半时，全局误差缩小为原来的 $1/16$ 。

2.7 稳定性分析

将 RK4 作用于 $\dot{y} = \lambda y$，逐级带入斜率表达式 ： $h k_1 = z y_n$, $h k_2 = \left(z + \frac{z^2}{2}\right) y_n$, $h k_3 = \left(z + \frac{z^2}{2} + \frac{z^3}{4}\right) y_n$, $h k_4 = \left(z + z^2 + \frac{z^3}{2} + \frac{z^4}{4}\right) y_n$ 。 代入更新式整理得到**四阶稳定性多项式** ： $$R_4(z) = 1 + z + \frac{z^2}{2!} + \frac{z^3}{3!} + \frac{z^4}{4!}$$ 其绝对稳定域满足 $|R_4(z)| \le 1$，在负实轴上的截距延伸至 $z \approx -2.785$ 。虽然稳定域显著大于欧拉法，但边界依然是有界的，因此非 A-稳定 。

2.8 数值含义与可验证预测

RK4 是经典非刚性问题的“高精度工作马” 。在双对数误差图上，拟合斜率 $p_{\text{obs}}$ 严格收敛至 **4.00**。

---

3. 隐式欧拉法 (Implicit Euler)

3.1 推导目标

推导隐式欧拉更新格式 $y_{n+1} = y_n + h f(t_{n+1}, y_{n+1})$，证明其局部误差 $O(h^2)$、全局误差 $O(h)$，以及 A-稳定性 。

3.2 假设与适用条件

$f(t, y)$ 满足 Lipschitz 条件，且具有连续偏导数，允许构造非线性残差雅可比矩阵 $J_F$ 。

3.3 符号定义

未知量设为未来的状态 $w = y_{n+1} \in \mathbb{R}^d$ 。

3.4 从第一原理出发

- **途径 A（右端点矩形法则）**：逼近积分 $\int_{t_n}^{t_{n+1}} f(t, y(t)) \mathrm{d}t \approx h f(t_{n+1}, y(t_{n+1}))$。
- **途径 B（向后泰勒展开）**：将精确解 $y(t_n) = y(t_{n+1} - h)$ 在未知的 $t_{n+1}$ 处向后展开 ： $$y(t_n) = y(t_{n+1}) - h y'(t_{n+1}) + \frac{1}{2} h^2 y''(\xi_{n+1}) = y(t_{n+1}) - h f(t_{n+1}, y(t_{n+1})) + \frac{1}{2} h^2 y''(\xi_{n+1})$$

3.5 连续模型到离散格式

移项并省略高阶项，得到隐式递推格式 ： $$\mathbf{y_{n+1} = y_n + h f(t_{n+1}, y_{n+1})}$$

3.6 隐式代数方程与牛顿迭代求解 (Newton's Method)

由于未知数 $w = y_{n+1}$ 封包在非线性函数 $f$ 内部，无法直接求解 。移项构造非线性残差函数 $F(w) = \mathbf{0}$ ： $$F(w) = w - y_n - h f(t_{n+1}, w) = \mathbf{0}$$ 求 $F(w)$ 关于 $w$ 的导数，得到残差雅可比矩阵 $J_F(w)$ ： $$J_F(w) = \frac{\partial F}{\partial w} = I - h J_f(t_{n+1}, w)$$  在每一步积分中，通过线性化求解牛顿更新量 $\delta^{(k)}$ ： $$\left( I - h J_f(t_{n+1}, w^{(k)}) \right) \delta^{(k)} = - \left( w^{(k)} - y_n - h f(t_{n+1}, w^{(k)}) \right)$$ $$w^{(k+1)} = w^{(k)} + \delta^{(k)}$$

3.7 误差与全局阶数

- 向后单步缺陷：$d_{n+1} = - \frac{1}{2} h^2 y''(\xi_{n+1}) + O(h^3) \implies \|d_{n+1}\| \le C h^2 = O(h^2)$ 。
- 假设代数方程精确求解，隐式误差递推关系为 $(1 - h L) \|e_{n+1}\| \le \|e_n\| + C h^2$ 。
- 设放大因子 $q = (1 - h L)^{-1}$，在 $h L \le 1/2$ 时满足 $q \le e^{2 h L}$ 。累积 $N$ 步得到： $$\|e_N\| \le C T e^{2 L T} h = O(h)$$**结论**：隐式欧拉法依然是**一阶精度** $p=1$ 。采用未来的斜率改变的是稳定性，而非精度的阶数 。

3.8 稳定性分析 (A-Stability & L-Stability)

带入测试方程 $\dot{y} = \lambda y$，移项整理 ： $$y_{n+1} = y_n + h \lambda y_{n+1} \implies (1 - z) y_{n+1} = y_n \implies R(z) = \frac{1}{1 - z}$$ 绝对稳定域为 $|R(z)| \le 1 \iff |z - 1| \ge 1$，即**复平面上以** $+1$ **为圆心、半径为** $1$ **的圆盘外部的无限大区域** 。

- **A-稳定性**：包含了整个复左半平面 $\{\mathbb{Re}(z) \le 0\}$，无条件无数值发散风险 。
- **L-稳定性**：当 $z \to -\infty$ 时，$\lim_{z \to -\infty} R(z) = 0$，能够无限衰减极硬的高频快模态 。