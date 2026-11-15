变系数与间断扩散椭圆边值问题 理论基础

包含连续模型、弱形式适定性、守恒有限差分、界面传导率、M‑矩阵理论、P₁有限元对照
目录

• 1 连续数学模型

• 2 强形式与界面传输条件

• 3 变分(弱)形式与Lax‑Milgram适定性

• 4 守恒有限差分(有限体积)离散

• 5 截断误差与光滑系数二阶相容性

• 6 间断系数：调和平均 vs 算术平均

• 7 Dirichlet边界对称消元

• 8 离散代数性质：SPD、M‑矩阵、离散最大值原理

• 9 离散稳定性与收敛估计

• 10 谱条件数：网格与材料对比度

• 11 P₁协调有限元对照理论

• 12 Interface‑PINN简要理论

1 连续数学模型

单位正方形区域 \Omega=(0,1)^2，边界 \partial\Omega=\Gamma_D，散度形式椭圆边值问题：

\begin{cases}
-\nabla\cdot\big(a(x,y)\nabla u(x,y)\big)=f(x,y),&\text{in }\Omega\\
u(x,y)=g(x,y),&\text{on }\partial\Omega
\end{cases}

符号说明

• u：标量物理势（温度、水力水头）

• f\in L^2(\Omega)：体积源项

• g\in H^{1/2}(\partial\Omega)\cap C^0(\partial\Omega)：Dirichlet边界数据

• 扩散通量：\boldsymbol j = -a\nabla u
一致椭圆假设：扩散系数几乎处处满足

0<a_{\min}\le a(x,y)\le a_{\max}<\infty,\quad \text{a.e. }(x,y)\in\Omega

定义材料对比度：\varrho_a = \dfrac{a_{\max}}{a_{\min}} \ge 1。
非散度形式仅当 a\in C^1(\bar\Omega) 成立：
-\nabla\cdot(a\nabla u) = -a\Delta u -\nabla a\cdot\nabla u = f
当系数存在跳跃间断，\nabla a 含有Dirac‑δ分布，点态非散度方程失效，必须使用积分守恒或弱形式。
2 强形式与界面传输条件

区域被内界面 \Sigma 分割为 \Omega_1,\Omega_2，\Sigma=\partial\Omega_1\cap\partial\Omega_2，分段强形式：

\begin{cases}
-\nabla\cdot(a\nabla u)=f,&\text{in }\Omega_1\cup\Omega_2\\
\llbracket u\rrbracket_\Sigma = u|_{\Omega_1}-u|_{\Omega_2}=0,&\text{势连续}\\
\llbracket -a\nabla u\cdot n_\Sigma\rrbracket_\Sigma = 0,&\text{法向通量连续}
\end{cases}

n_\Sigma：由 \Omega_1 指向 \Omega_2 的单位法向量。数值离散必须同时逼近势连续与法向通量连续两个界面条件。

3 变分(弱)形式与Lax‑Milgram适定性

对边界数据做提升：\tilde g\in H^1(\Omega)，满足迹条件 \tilde g|_{\partial\Omega}=g。
分解解：u = u_0+\tilde g，其中 u_0\in H_0^1(\Omega)。

定义双线性形式与线性泛函

\mathcal B(w,v)=\int_\Omega a(x,y)\nabla w\cdot\nabla v\,\mathrm{d}x\mathrm{d}y,\quad
\ell(v)=\int_\Omega f(x,y)v(x,y)\,\mathrm{d}x\mathrm{d}y

弱问题：求 u_0\in H_0^1(\Omega)，使得

\mathcal B(u_0,v)=\ell(v)-\mathcal B(\tilde g,v),\quad \forall v\in H_0^1(\Omega)

Lax‑Milgram引理条件

1. 连续性
|\mathcal B(w,v)|\le a_{\max}\|w\|_{H^1(\Omega)}\|v\|_{H^1(\Omega)}
2. 强制性，利用Poincaré‑Friedrichs不等式
\mathcal B(v,v)\ge a_{\min}\|\nabla v\|_{L^2}^2 \ge \frac{a_{\min}}{1+C_P^2}\|v\|_{H^1}^2
C_P 为Poincaré常数，单位正方形 C_P=\dfrac{1}{\sqrt{2}\pi}。

3. \ell(v) 在 H_0^1(\Omega) 上有界。
适定性定理：满足一致椭圆假设下，弱问题存在唯一解 u\in H^1(\Omega)。齐次边界下稳定性估计：
\|\nabla u\|_{L^2(\Omega)}\le \frac{C_P}{a_{\min}}\|f\|_{L^2(\Omega)}
连续最大值原理：若 f\equiv0，解的极值全部取在边界：

\min_{\partial\Omega}g \le u(x,y)\le \max_{\partial\Omega}g,\quad \forall(x,y)\in\bar\Omega

4 守恒有限差分(有限体积)离散

均匀笛卡尔网格，每轴剖分 N 段，网格步长 h=1/N；每维内部节点 n=N-1。
网格节点 x_{ij}=(ih,jh)；围绕每个内点构造对偶控制体：

K_{ij}=\big[x_{i-1/2},x_{i+1/2}\big]\times\big[y_{j-1/2},y_{j+1/2}\big],\quad |K_{ij}|=h^2

控制体积分+高斯散度定理

\int_{K_{ij}}-\nabla\cdot(a\nabla u)\mathrm{d}x\mathrm{d}y
=\int_{\partial K_{ij}} \boldsymbol j\cdot n \mathrm{d}s
=\int_{K_{ij}}f\mathrm{d}x\mathrm{d}y

定义面数值通量

F_{i+1/2,j} = -a_{i+1/2,j}\frac{U_{i+1,j}-U_{ij}}{h}

得到守恒五点离散算子

(A_h U)_{ij}=
\frac1{h^2}\Big[
a_\Sigma^{(i,j)}U_{ij}
-a_W U_{i-1,j}
-a_E U_{i+1,j}
-a_S U_{i,j-1}
-a_N U_{i,j+1}
\Big]=f_{ij}

其中 a_\Sigma^{(i,j)}=a_{i-1/2,j}+a_{i+1/2,j}+a_{i,j-1/2}+a_{i,j+1/2}，为四个面传导系数之和。
当 a\equiv1，模板退化为标准五点Laplace差分。
网格‑向量映射

行主序(ij索引)
k=\phi(i,j)=(i-1)n+(j-1),\quad 1\le i,j\le n
相邻节点偏移：东西方向 \pm n，南北方向 \pm 1。
组装矩阵为块三对角稀疏矩阵；非零元总数：nnz(A_h)=5n^2-4n，存储采用CSR稀疏格式。

5 截断误差与光滑系数二阶相容性

局部截断误差定义：将解析解节点值代入离散算子

\tau_{ij}(u) := (A_h u)_{ij} - \big(-\nabla\cdot(a\nabla u)\big)(x_{ij})

定理：光滑系数二阶相容性
若 a\in C^5(\bar\Omega)，解析解 u\in C^6(\bar\Omega)，采用中点采样或算术平均构造面传导，则

\tau_{ij}(u)=\mathcal O(h^2),\quad h\to0

备注：仿射系数如 a=1+x，算术平均等价中点采样；该测试无法暴露 \theta a_{xx} 修正项，只有带二阶导数的系数才能区分算术平均与中点求值差异。
6 间断系数：调和平均 vs 算术平均

网格边被界面切割，边左右扩散系数 a_L,a_R；边内两段长度 d_L+d_R=h。

串联电阻推导调和平均等效面传导


a_E^{\text{harm}}=\frac{h}{\dfrac{d_L}{a_L}+\dfrac{d_R}{a_R}}

界面恰好平分网格边 d_L=d_R=h/2：

a_E^{\text{harm}}=\frac{2a_L a_R}{a_L+a_R}

算术平均：

a_E^{\text{arith}}=\frac{a_L+a_R}{2}

平分界面下二者相对误差：

\frac{a_E^{\text{arith}}-a_E^{\text{harm}}}{a_E^{\text{harm}}}=\frac{(a_L-a_R)^2}{4a_L a_R}

该误差与网格步长h无关，属于O(1)量级面传导误差。

关键结论

1. 调和平均：层状分片线性基准，界面平分网格边时，节点解可达机器精度，界面通量与解析通量一致。

2. 算术平均：矩阵依旧对称、局部面通量守恒、满足M‑矩阵；但界面通量存在显著误差；二维Dirichlet算例中最大界面通量误差不随网格加密消失，节点误差仅一阶收敛。

3. ⚠️仅校验矩阵对称、重构两侧通量跳跃接近零不足以证明界面物理条件正确。
网格奇偶约定：FDM间断测试使用奇数N，界面切过网格边；FEM层状测试使用偶数N，界面对齐单元边界。
7 Dirichlet边界对称消元

1. 朴素行替换（弃用）：保留边界作为未知量，边界行替换为单位行；破坏矩阵对称性，不能使用CG、Cholesky。

2. 对称内部消元（本文采用）：仅内部节点作为未知；边界已知值移到右端向量\boldsymbol b，边界项带上对应面传导权重。


b_k = f_{ij}+\frac1{h^2}\Big[
\delta_{i,1}a_{1/2,j}g_{0,j}
+\delta_{i,n}a_{n+1/2,j}g_{N,j}
+\delta_{j,1}a_{i,1/2}g_{i,0}
+\delta_{j,n}a_{i,n+1/2}g_{i,N}
\Big]

该处理不引入额外边界截断误差，维持全局二阶精度。

8 离散代数性质：SPD、M‑矩阵、离散最大值原理
定理（对称Dirichlet消元后A_h）
1. 对称性 A_h=A_h^T：每条网格边共用同一个面传导系数，算术/调和平均均满足。

2. 对称正定SPD，离散能量恒等式

v^T A_h v
=\frac1{h^2}\sum_{e\in\mathcal E_{\text{int}}}a_e(v_k-v_l)^2
+\frac1{h^2}\sum_{b\in\mathcal E_{\text{bdry}}}a_b v_k^2>0,\quad \forall v\neq \boldsymbol 0

3. M‑矩阵：对角元严格正，非对角元\le0；边界邻近行严格对角占优；网格图连通，不可约对角占优，逆矩阵全部元素严格大于零 A_h^{-1}>0。

4. 离散最大值原理(DMP)：f\equiv0时

\min_{\Gamma_h}g_{ij}\le U_{ij}\le \max_{\Gamma_h}g_{ij}

⚠️重要实践启示：
矩阵对称、M‑矩阵、离散最大值原理仅仅是必要条件，不是充分条件。算术平均格式全部满足上述代数性质，但界面通量物理结果错误。
9 离散稳定性与收敛估计

误差定义 e = U - u_{\text{exact}}，误差方程 A_h e = -\tau。

1. 能量范数稳定性：最小特征值下界 \lambda_{\min}(A_h)\ge 8a_{\min}

\|e\|_{h,2} \le \frac{C_{\text{LTE}}}{8a_{\min}} h^2

2. 最大范数稳定性
❗Loewner谱序不能推导出逐元素矩阵大小关系，A_h\succeq a_{\min}A_h^{(1)} 不蕴含 A_h^{-1}\le a_{\min}^{-1}(A_h^{(1)})^{-1}。
需要障碍函数论证，存在与h无关常数C_{\text{stab}}

\|e\|_\infty \le C_{\text{stab}} C_{\text{LTE}} h^2

该收敛理论仅适用于系数和解充分光滑场景；层状间断问题 u\notin H^2(\Omega)，不能用这套渐近阶，改用节点精确性定理。
10 谱条件数：网格与材料对比度

瑞利商上下界

a_{\min}\frac{v^T A_h^{(1)}v}{v^T v}
\le \frac{v^T A_h v}{v^T v}
\le a_{\max}\frac{v^T A_h^{(1)}v}{v^T v}

A_h^{(1)} 常系数离散Laplace矩阵。

条件数上界

\kappa_2(A_h) \le \varrho_a \cdot \kappa_2(A_h^{(1)}) = \varrho_a \cdot \mathcal O(h^{-2})

• 固定对比度，加密网格：条件数 \mathcal O(h^{-2})，CG迭代步数正比 \sqrt{\kappa_2}。

• 固定网格，增大材料对比度：条件数线性增长；Jacobi预条件可显著削弱对比度带来的迭代压力。

11 P₁协调有限元对照理论

对同一变分问题，采用Friedrichs‑Keller三角剖分，每个正方形沿对角线切分两个直角三角形。
试探‑测试空间

V_{0h}=\{v_h\in C^0(\bar\Omega): v_h|_T\in P_1(T),\ v_h|_{\partial\Omega}=0\}

Galerkin刚度矩阵

(A_h^{\text{FEM}})_{kl}=
\sum_{T\in\mathcal T_h}(\nabla\varphi_k|_T\cdot\nabla\varphi_l|_T)\int_T a(x,y)\,\mathrm{d}x\mathrm{d}y

性质

1. 继承双线性形式，天然对称正定。

2. 光滑解析解收敛阶：\|u-u_h\|_{H^1}=\mathcal O(h)，\|u-u_h\|_{L^2}=\mathcal O(h^2)。

3. 层状间断：单元边界与材料界面对齐时，分片线性解析解属于有限元空间，可以得到节点精确解；但单元内部单侧通量依然会跳跃；弱形式保证积分意义平衡，不保证点态通量连续。

12 Interface‑PINN简要理论

采用两套独立MLP子网分别表示界面两侧子区域；损失函数由三部分构成：

1. PDE残差损失；

2. 外边界Dirichlet条件损失；

3. 界面软惩罚约束：势连续、法向通量连续（惩罚项，非硬等式约束）。
注意：软惩罚无法数学严格保证界面条件成立；针对本报告分片线性层状基准，Interface‑PINN不能超越调和FDM与对齐网格P₁‑FEM的精度。
