"""极分解正交因子的梯度流模型，以及独立的有限时间诊断量。

状态向量采用列优先展开：``y = X.reshape(-1, order='F')``。
精确解只用于验证，不参与数值求解器的推进。
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


Array = NDArray[np.float64]


def rotation(theta: float) -> Array:
    """返回绕第三坐标轴旋转 theta 弧度的 3×3 矩阵。"""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def benchmark(singular_values: tuple[float, float, float] = (0.2, 1.4, 3.0)) -> Array:
    """构造题目 ⑤ 的基准初值；首个奇异值取零时得到秩亏版本。"""
    return rotation(0.4) @ np.diag(singular_values) @ rotation(-0.7).T


def vectorize(x: Array) -> Array:
    """按列优先顺序将矩阵展开成一维状态向量。"""
    return np.asarray(x, dtype=float).reshape(-1, order="F")


def unvectorize(y: Array) -> Array:
    """按列优先顺序将状态向量还原为方阵。"""
    n = int(np.sqrt(y.size))
    if n * n != y.size:
        raise ValueError("状态向量长度必须是完全平方数")
    return np.asarray(y, dtype=float).reshape((n, n), order="F")


def matrix_rhs(x: Array) -> Array:
    """计算矩阵方程右端 f(X)=X(I-X^T X)。"""
    return x @ (np.eye(x.shape[1]) - x.T @ x)


def rhs(t: float, y: Array) -> Array:
    """向量化的常微分方程右端，供三种积分器和 Radau 调用。"""
    del t  # 方程是自治的，但保留标准初值问题接口 f(t, y)。
    return vectorize(matrix_rhs(unvectorize(y)))


def frechet(x: Array, h: Array) -> Array:
    """计算方向 H 上的 Fréchet 导数 Df(X)[H]。"""
    return h @ (np.eye(x.shape[1]) - x.T @ x) - x @ (h.T @ x + x.T @ h)


def jacobian(t: float, y: Array) -> Array:
    """在与 ``rhs`` 一致的列优先基下组装解析 Jacobian。"""
    del t
    x = unvectorize(y)
    n = x.shape[0]
    columns = []
    for j in range(n):
        for i in range(n):
            h = np.zeros_like(x)
            h[i, j] = 1.0
            columns.append(vectorize(frechet(x, h)))
    return np.column_stack(columns)


def exact_matrix(t: float | Array, x0: Array) -> Array:
    """根据初值 SVD 返回经过时间 ``t`` 后的精确矩阵；允许零奇异值。"""
    t_array = np.asarray(t, dtype=float)
    if np.any(t_array < 0):
        raise ValueError("经过时间 t 必须非负")
    u, s0, vt = np.linalg.svd(x0, full_matrices=False)
    decay = np.exp(-2.0 * t_array[..., None])
    s = s0 / np.sqrt(s0**2 + (1.0 - s0**2) * decay)
    return np.einsum("ik,...k,kj->...ij", u, s, vt)


def energy(x: Array) -> float:
    """计算 Lyapunov 函数 Phi(X)=||X^T X-I||_F^2/4。"""
    defect = x.T @ x - np.eye(x.shape[1])
    return float(np.linalg.norm(defect, "fro") ** 2 / 4.0)


def orthogonality_defect(x: Array) -> float:
    """计算正交性缺陷 ||X^T X-I||_F。"""
    return float(np.linalg.norm(x.T @ x - np.eye(x.shape[1]), "fro"))


def lyapunov_rate(x: Array) -> float:
    """计算连续流的瞬时能量导数 dPhi/dt=-||f(X)||_F^2。"""
    return -float(np.linalg.norm(matrix_rhs(x), "fro") ** 2)


def singular_values(x: Array) -> Array:
    """返回矩阵的奇异值，顺序与 NumPy SVD 一致（降序）。"""
    return np.linalg.svd(x, compute_uv=False)
