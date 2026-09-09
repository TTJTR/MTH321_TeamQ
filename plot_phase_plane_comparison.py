import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from euler_skeleton import solve_euler

# 1. 定义 Van der Pol (mu=1) 的右端项
def vanderpol_rhs(t, y, mu=1.0):
    return np.array([y[1], mu * (1.0 - y[0]**2) * y[1] - y[0]])

# 初始状态与时间设置
y0 = np.array([0.5, 0.0])
t0, t1 = 0.0, 20.0  # 延长积分时间到 20.0 以确保完整画出外围的极限环
h_euler = 0.1       # 设定显式欧拉的对比步长

# 2. 构建高精度 Oracle (Reference)
sol = solve_ivp(vanderpol_rhs, [t0, t1], y0, method="DOP853", 
                rtol=1e-12, atol=1e-14, dense_output=True)
t_ref = np.linspace(t0, t1, 2000)
y_ref = sol.sol(t_ref)

# 3. 计算显式欧拉解 (Euler h=0.1)
t_euler, y_euler = solve_euler(vanderpol_rhs, y0, t0, t1, h_euler)

# 4. 绘制对比相图
fig, ax = plt.subplots(figsize=(8, 5.5))

# 绘制 Reference (实线)
ax.plot(y_ref[0], y_ref[1], '-', color='dimgray', label='reference')

# 绘制 Euler h=0.1 (虚线)
ax.plot(y_euler[:, 0], y_euler[:, 1], '--', color='teal', label=f'Euler h={h_euler}')

# 标记初始状态点 (0.5, 0)
ax.plot(y0[0], y0[1], 'o', color='dimgray', markersize=5, label='initial state')

# 设置图表格式以匹配幻灯片风格
ax.set_xlabel('y1')
ax.set_ylabel('y2')
ax.set_title('Van der Pol: phase-plane trajectory', fontsize=14, loc='left', pad=15)
ax.legend(loc='upper left', framealpha=1.0)
ax.grid(True, linestyle=':', alpha=0.6)

# 添加幻灯片底部的说明文字
caption_text = ("The marked starting point is (0.5, 0). The reference moves outward toward the attracting\n"
                "oscillation.")
fig.text(0.1, 0.02, caption_text, fontsize=10, color='dimgray')
plt.subplots_adjust(bottom=0.18) # 腾出底部空间放置文字

# 遵循课程可视化规范，使用固定文件名和分辨率保存图表
fig.savefig("vanderpol_phase_plane_comparison.png", dpi=150)
print("-> 对比相图已保存为 'vanderpol_phase_plane_comparison.png'")