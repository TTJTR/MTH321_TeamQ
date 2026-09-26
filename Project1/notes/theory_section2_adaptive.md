### A. 资料核对

- **已参考课程资料**：
    
      
    - `image_66a89a.png`（Tiered tasks 列表）：明确列出基础任务“$\star$ Basic adaptive step-size control with a stated tolerance”。
        
          
        
    - 课程讲义及课件（Griffiths & Higham Ch. 11、Butcher Ch. 3/4、Week 2 Adaptivity slides 及 Week 2 Discussion/Tutorial）：规定了步长加倍（Step-doubling）两路对比机制、理查森外推（Richardson extrapolation）局部截断误差估计、混合容差（Mixed atol/rtol）与归一化误差度量，以及步长重调安全因子与截断范围。
        
          
        
          
        
- **缺失资料 / 需查证事项**：无。
    
      
    

### B. **核心目标**

- **核心目标**：从第一原理出发，建立步长加倍（Step-doubling / Richardson Extrapolation）**与**嵌入式对（Embedded Pairs）的局部截断误差（LTE）估计模型；推导最优步长预测公式 $h_{\text{new}} \propto (\text{tol}/E)^{\frac{1}{p+1}}$ 的来源；严格推导步长接受/拒绝准则与安全因子的代数设计。

### C. 知识点讲解：自适应步长控制的完整数学推导

#### 1. 推导目标

推导自适应步长控制器的局部误差估计公式、基于理查森外推（Richardson Extrapolation）的系数标定、误差归一化准则、以及基于极值优化的步长调整律（Step-size update formula）。

  

#### 2. 假设与适用条件

- 右端项 $f(t, y)$ 至少具有 $C^{p+1}$ 阶连续偏导数，确保局部截断误差在小步长极限下满足严谨的渐近泰勒展开 $C(t) h^{p+1} + \mathcal{O}(h^{p+2})$。
    
      
    
- **局部化假设（Localizing Assumption）**：在考察当前步 $[t_n, t_n + h]$ 时，假设输入的起始状态 $y_n$ 是精确的基准，即 $y_n = y(t_n)$。
    
      
    
- 系统必须具有慢度或平滑度变化的非一致时间尺度（例如 Topic 5 的极分解流：初始瞬态变化极快，后期逼近正交矩阵时趋于平缓）。
    
      
    

#### 3. 符号定义

- $y(t)$：连续理论轨迹。
    
      
    
- $y_c$（Coarse solution）：从 $(t_n, y_n)$ 出发，以步长 $h$ 走一步得到的解。
    
      
    
- $y_f$（Fine solution）：从 $(t_n, y_n)$ 出发，以步长 $h/2$ 连续走两步得到的解。
    
      
    
- $\delta_h$：以步长 $h$ 走一步的单步局部截断误差（One-step defect）。
    
      
    
- $\text{atol}, \text{rtol}$：用户给定的绝对容差与相对容差。
    
      
    
- $E$：无量纲化的归一化误差比率。
    
      
    
- $S$（或 $\beta$）：安全系数（Safety factor，通常取 $0.8 \sim 0.9$）。
    
      
    

#### 4. 从第一原理出发：理查森外推与误差估计

设底层数值积分器的阶数为 $p$。根据局部截断误差定义，从精确起点 $y(t_n)$ 出发走一步 $h$，数值解的泰勒展开余项满足：

  

$$y(t_n + h) - \Phi_h(t_n, y_n) = \psi(t_n) h^{p+1} + \mathcal{O}(h^{p+2})$$

其中主误差系数 $\psi(t_n)$ 仅取决于高阶导数，在局部区间内近似为常数。

  

**途径 A：粗步解（One full step of size $h$）**

走一步全步长 $h$，得到的粗解为：

  

$$y_c = y(t_n + h) - \psi(t_n) h^{p+1} + \mathcal{O}(h^{p+2})$$

**途径 B：精步解（Two half-steps of size $h/2$）**

  

- 第一半步从 $t_n$ 到 $t_n + h/2$：
    
      
    
    $$y_{1/2} = y\left(t_n + \frac{h}{2}\right) - \psi(t_n) \left(\frac{h}{2}\right)^{p+1} + \mathcal{O}(h^{p+2})$$
    
- 第二半步从 $t_n + h/2$ 到 $t_n + h$。由于两步距离极短，导数主项系数相同，两步的局部截断误差线性叠加：
    
      
    
    $$y_f = y(t_n + h) - 2 \cdot \psi(t_n) \left(\frac{h}{2}\right)^{p+1} + \mathcal{O}(h^{p+2}) = y(t_n + h) - \frac{\psi(t_n) h^{p+1}}{2^p} + \mathcal{O}(h^{p+2})$$
    

**两路解相减（消除未知真实解 $y(t_n + h)$）**：

  

$$y_c - y_f = -\psi(t_n) h^{p+1} \left(1 - \frac{1}{2^p}\right) + \mathcal{O}(h^{p+2}) = -\frac{2^p - 1}{2^p} \psi(t_n) h^{p+1} + \mathcal{O}(h^{p+2})$$

由此反解出未知的主误差项 $\psi(t_n) h^{p+1}$：

  

$$\psi(t_n) h^{p+1} \approx \frac{2^p}{2^p - 1} (y_f - y_c)$$

因此，**精解 $y_f$ 相对于真实解的局部误差**可以极其精确地估计为：

  

$$\hat{e}_f = y(t_n + h) - y_f \approx \frac{\psi(t_n) h^{p+1}}{2^p} = \frac{y_f - y_c}{2^p - 1}$$

  

- 当算法为隐式/显式欧拉法（$p=1$）时：分母为 $2^1 - 1 = 1$，即：
    
      
    
    $$\hat{e}_f \approx y_f - y_c$$
    
      
    
- 当算法为经典 RK4（$p=4$）时：分母为 $2^4 - 1 = 15$，即：
    
      
    
    $$\hat{e}_f \approx \frac{y_f - y_c}{15}$$
    
      
    

#### 5. 归一化标尺与误差度量（Normalized Error Ratio）

在向量系统或矩阵问题中，各分量的数值量级可能相差悬殊。为了让误差判定无量纲化，引入混合容差标尺向量 $s$：

  

$$s_i = \text{atol}_i + \text{rtol} \cdot \max(\vert{}y_{n,i}\vert{}, \vert{}y_{f,i}\vert{})$$

  

采用无穷范数（或加权 2-范数）计算当前试探步的归一化误差标量 $E$：

  

$$E = \max_{i} \left\vert{} \frac{\hat{e}_{f,i}}{s_i} \right\vert{}$$

  

- 若 $E \le 1$：说明每分量的局部误差均严格控制在容许带宽内，**接受该步（Accept）**。
    
      
    
- 若 $E > 1$：说明局部误差超标，**拒绝该步（Reject）**。
    
      
    

#### 6. 步长调节定律的渐近推导（Step-size Update Formula）

我们探究：在下一阶段，什么样的理想步长 $h_{\text{opt}}$ 能够使得单步误差恰好等于容差（即理想的 $E_{\text{target}} \approx 1$）？

根据第 4 步的渐近理论，误差与步长呈 $(p+1)$ 次方幂律关系：

  

$$E(h) = K \cdot h^{p+1}$$

  

若用新步长 $h_{\text{new}}$，产生的归一化误差期望为目标值 $1$：

  

$$1 = K \cdot h_{\text{new}}^{p+1}$$

  

两式相除消除未知常数 $K$：

  

$$\frac{1}{E} = \left(\frac{h_{\text{new}}}{h}\right)^{p+1} \implies h_{\text{new}} = h \cdot \left(\frac{1}{E}\right)^{\frac{1}{p+1}} = h \cdot E^{-\frac{1}{p+1}}$$

  

**控制论修正（工程保护与安全因子）**： 纯理论公式是在 $h \to 0$ 渐近线上建立的，直接应用极易引发“步长激增 $\to$ 下一步被拒绝 $\to$ 步长骤降”的高频抖动震荡。因此在实际代码中必须施加三道安全防线：

  

1. **安全因子 $S \in [0.8, 0.9]$**：预留 $10\% \sim 20\%$ 的保守余量，降低下一步被拒绝的概率。
    
      
    
2. **变化比率裁剪（Clipping / Clamping）**：限制单步步长缩放因子的最大与最小值，避免剧烈波动：
    
      
    
    $$r = \text{clip}\left(S \cdot E^{-\frac{1}{p+1}}, \, r_{\min}, \, r_{\max}\right)$$
    
    常用经验常数为 $r_{\min} = 0.2$（防止步长坍缩过快），$r_{\max} = 2.0$ 或 $5.0$（防止步长盲目膨胀）。
    
      
    
3. **防除零保护**：当解进入绝对静止区导致 $E \to 0$ 时，直接取 $r = r_{\max}$。
    
      
    

综上，完整的下一代步长递推公式为：

  

$$h_{\text{new}} = h \cdot \min\left(r_{\max}, \, \max\left(r_{\min}, \, S \cdot E^{-\frac{1}{p+1}}\right)\right)$$

  

#### 7. 稳定性与刚性控制（自适应控制器的隐式物理响应）

对于显式方法（如 Explicit Euler 或 RK4），当系统进入刚性区间（例如 Topic 5 中初始奇异值极大导致的快速瞬态），系统的局部特征值绝对值很大。

  

- 如果步长 $h$ 试图跨越显式稳定边界（如欧拉法 $\vert{}1 + h\lambda\vert{} > 1$），解会产生急剧的数值放大。
    
      
    
- 这一失稳趋势会瞬间在 $y_f - y_c$ 的差值中产生巨大尖峰（$E \gg 1$）。
    
      
    
- 自适应控制器捕获到这一信号后，会**强制触发拒步重试，并以 $E^{-\frac{1}{p+1}}$ 的比例剧烈缩减步长**，直到 $h$ 重新落回到绝对稳定域内部！
    
      
    
- 这就是自适应步长控制器能够“自动嗅探并贴合稳定边界”的深层控制论机制。
    
      
    

#### 8. 结论及其数值含义

1. **局部外推（Local Extrapolation）**：一旦判定 $E \le 1$，最终前进的状态应更新为精步解 $y_{n+1} = y_f$ 而不是 $y_c$。因为 $y_f$ 自身的理论精度达到了更高的一阶，外推推进能显著提升全局解质量。
    
      
    
2. **被拒步的处理铁律**：若 $E > 1$，**严禁推进时间 $t$ 或状态 $y$**，必须在当前基准点 $(t_n, y_n)$ 上原地减小步长重试（_“A rejected step has not happened”_）。
    
      
    
3. **算力与精度的权衡**：步长加倍法每一步需要做 3 次子步评估（1 次全步 + 2 次半步），相当于计算量翻倍；但在奇异性或刚性多尺度问题中，它避免了盲目定步长的发散风险，总体能用少得多的总步数完成全域积分。
    
      
    