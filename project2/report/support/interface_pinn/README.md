# Interface PINN evidence and replay

This folder supports the advanced-method section of the locally merged report.
The three c=10 seeds (11, 22, 33) were copied from the local server archive
`Project2/results_20261029/I-PINNs/runs/server_interface/`. Matching model
source and source hashes are supplied. Checkpoints are retained unchanged.

From `project2/report`, with NumPy, SciPy, PyTorch and Matplotlib installed:

```text
python support/interface_pinn/reevaluate.py
python support/interface_pinn/make_figures.py
```

The first command loads checkpoints on CPU and solves harmonic FDM N=63 and
interface-fitted P1 FEM N=64 using sparse LU. Solution errors use 3,844 common
interior points (i/63,j/63), i,j=1,...,62. The metric is the unweighted
sampled relative Euclidean norm, not an integrated continuous L2 norm.
FEM uses its P1 interpolant. Flux error is the maximum absolute error at 62
interface points with +x orientation and exact flux -20/11. FDM uses the
shared face flux; FEM and PINN use both one-sided traces. PINN metrics are
averaged after evaluating each seed, not after averaging predictions.

The archived environment records PyTorch 2.8.0+cu128 on an A100-PCIE-40GB.
The local replay used PyTorch 2.7.1+cpu; it does not retrain the model.
Archive metadata are preserved as recorded rather than inferred from the
replay machine. Training comprises 10,000 Adam steps plus L-BFGS max_iter=500.
Only periodic Adam losses and the final L-BFGS objective are available;
there is no solution-error-versus-step or per-step timing history.

The implementation has two independent tanh subnetworks, unlike the
shared-parameter architecture in the cited I-PINNs paper. The comparison
uses different mesh parities by design and is not at equal DOF or compute.
Classical exactness is specific to this piecewise-linear benchmark.
