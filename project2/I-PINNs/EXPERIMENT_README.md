# Project 2: variable diffusion and interface-aware PINNs

第 3 题实验框架：保守 FDM 基线 + 界面 PINN + 单网络 PINN 对照。

**方法名称边界：** 当前是通用的双网络、软界面约束 PINN，不声称完整复现论文 `Interface PINNs (I-PINNs): A physics-informed neural networks framework for interface problems`。在拿到全文、核对网络构造与训练细节之前，请在报告中使用 `interface-aware PINN baseline`。参考入口：https://www.sciencedirect.com/science/article/pii/S0045782524003918 。

## 本地 dl 环境

在本目录执行：

```powershell
conda activate dl
python -m unittest discover -s tests -v
python run_experiment.py --config configs/smoke.json --require-acceptance
```

如果 PowerShell 无法激活 conda，可以使用：

```powershell
conda run --no-capture-output -n dl python run_experiment.py --config configs/smoke.json --require-acceptance
```

已验证环境：Python 3.10.18 / PyTorch 2.7.1+cpu / NumPy 2.2.6 / SciPy 1.15.3。没有修改已有 dl 环境。依赖版本范围见 requirements.txt；它是可移植依赖清单，并非逐位可复现的锁文件。

## 服务器

上传整个目录（可不上传 runs/），在具有可用 PyTorch 的 Python 3.10+ 环境运行。根据服务器 CUDA/驱动安装对应 GPU PyTorch；不要把 Windows dl 环境直接复制到 Linux。

```bash
python -c "import torch; print(torch.__version__, torch.cuda.is_available())"
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run_experiment.py --config configs/smoke.json --device cuda --require-acceptance
python run_experiment.py --config configs/server.json --output runs/server_interface
python run_experiment.py --config configs/server.json --method single --output runs/server_single
python run_experiment.py --config configs/server.json --case smooth --fdm-only --output runs/server_smooth_fdm
```

先验证 CUDA，再安装缺失依赖。如果已有 GPU PyTorch 满足范围，pip 通常会保留它；requirements.txt 本身不选择 CUDA 发行版。`--device cuda` 在 CUDA 不可用时明确失败；server.json 的 `auto` 会选择 CUDA，否则回退 CPU。

server.json 是尚未全面验证的实验起点：系数比 1/10/100，种子 11/22/33，64 宽三隐藏层、10000 Adam 步 + 最多 500 L-BFGS 迭代。不要直接假设这些参数在高反差下达标。两组方法使用相同采样预算、损失权重和优化预算，但参数量不同，因此同时报告参数量、时间、误差；这不是等参数量对照。

输出目录必须不存在，防止覆盖旧实验。长任务可由服务器的 tmux/作业调度器管理。当前版本保存最终 checkpoint，不支持中断续训；无需分布式训练。

## 模型和离散

- 区域 `(0,1)^2`，全 Dirichlet 数据取解析解。
- smooth：`a=1+x`，`u=sin(pi*x) sin(pi*y)`，源项独立经自动微分检查；FDM 使用算术面平均。
- layered：界面 `x=0.5`，`a_L=1, a_R=c`，`f=0`。精确解左侧 `2c*x/(1+c)`，右侧 `c/(1+c)+2(x-0.5)/(1+c)`。默认 c=10 正是课件算例。其他 c 的实验是一族不同边界数据的制造解问题，不是固定边界下只改变材料。
- FDM：强消去 Dirichlet，自由度 `k=(i-1)(N-1)+(j-1)`；共享正面系数，组装稀疏 SPD 矩阵；分层算例 N 必须为奇数。算术平均只作为错误界面电阻的对照。
- PINN：两侧各一个 tanh MLP，输入映射为 `2z-1`，输出不施加硬边界；外边界、解连续、通量连续均为软损失。所有界面通量使用同一 +x 法向；物理通量 `q=-a du/dx`。
- 内部 PDE 损失除以局部 a，通量跳跃损失除以 `max(1,c)`；权重在配置中明确给出。该归一化会影响高反差实验，需做敏感性研究后再形成结论。
- 单网络对照也包含界面通量损失。全局光滑网络难以表示分层算例的导数跳变，这是该对照的结构限制。
- Adam 每步重新采样；L-BFGS 固定采样点，使线搜索面对确定目标。没有在系数跳变处对分段系数求强导数。

## 输出与解释

每次运行保存：已解析配置、UTC 时间、软硬件环境、源码 SHA256、计算前预测、FDM CSV/JSON、每个 PINN 的 checkpoint / training.csv / metrics.json / predictions.npz / 解与通量图，以及 summary.json。

- FDM L2：内部节点 `sqrt(h^2 sum(error^2))`；Linf：全节点最大误差。
- PINN L2：独立规则网格上的二维梯形求积；另报相对 L2、全域/边界最大误差、双侧界面解与物理通量跳跃、界面通量对精确解误差、独立移位网格上的各侧强 PDE 残差 RMS。两种 L2 定义明确不同，不直接冒充完全相同范数的比较。
- `accepted` 只代表配置中列出的工程冒烟阈值；不是数学收敛证明，也不表示课程验收。训练用完预算不称为“收敛”。默认记录未达标结果，便于诊断；`--require-acceptance` 未达标返回退出码 2。
- 谐均值分层基准会接近舍入误差，程序不对该误差拟合收敛阶。需要一般收敛验证时看 smooth 算例。
- CPU/GPU 的计时环境不同；PINN 时间包含训练但不包含初始化、作图与评估，FDM 分开记录组装与求解。CUDA 训练计时前后同步。

## 实验状态和待办

本地只验证小规模分层训练与 FDM；没有运行服务器全量配置，没有证明 ML 比 FDM 更快或更准。见 docs/local_verification.md。

下一阶段：核对 I-PINNs 全文；多种子统计与误差条；扩大反差及损失权重敏感性；提高训练预算并进行独立精度验收；若要作公平的 FDM/PINN 精度比较，应统一误差积分网格及计时口径。完整课程审计需要团队亲自核对、解释并签署，当前 AI 自检不能代替学生验收。
