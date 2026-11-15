"""Replay archived checkpoints and compare three methods on common sample sets.
No training. Solution norm is sampled nodal l2, not a continuous L2 integral.
"""
import importlib.util,json,sys
from pathlib import Path
import numpy as np
import torch
from scipy.sparse.linalg import spsolve
ROOT=Path(__file__).resolve().parents[2]
P2=ROOT.parent
from modelsrc.pinn import Solver
torch.set_num_threads(4)
spec=importlib.util.spec_from_file_location('disc',P2/'algorithm_section/src/discretisation.py')
disc=importlib.util.module_from_spec(spec);spec.loader.exec_module(disc)
N=63;c=10.
axis=np.arange(1,N)/N
x,y=np.meshgrid(axis,axis,indexing='ij')
z=np.column_stack([x.ravel(),y.ravel()])
truth=disc.exact(x,y,'layered',c).ravel()
rel=lambda u:float(np.linalg.norm(u-truth)/np.linalg.norm(truth))
out={'protocol':{'contrast':c,'solution_samples':'62 x 62 common interior nodes, x=i/63, y=j/63','solution_metric':'norm(pred-exact)/norm(exact), unweighted sampled l2','flux_samples':'62 common interface points, x=0.5, y=j/63','flux_metric':'max absolute physical flux error, common +x orientation','FDM_intervals':63,'FEM_intervals':64,'linear_solver':'SciPy sparse LU on CPU','PINN_seeds':[11,22,33],'note':'FEM is evaluated by its actual P1 interpolant. FDM is evaluated at its nodes. Different mesh parities are intentional; not an equal-budget benchmark.'}}
A,b,md=disc.assemble_fdm(N,'layered',c,'harmonic')
uf=disc.solution_grid(spsolve(A,b),md)
qx,_,_=disc.fdm_fluxes(uf,md)
out['FDM']={'relative_l2':rel(uf[1:-1,1:-1].ravel()),'flux_max_error':float(abs(qx[N//2,1:-1]+20/11).max())}
M=64
A,b,md=disc.assemble_fem(M,'layered',c)
ue=disc.solution_grid(spsolve(A,b),md)
# Exact P1 evaluation on the recorded lower-left to upper-right diagonal split.
xx=z[:,0]*M;yy=z[:,1]*M;i=np.floor(xx).astype(int);j=np.floor(yy).astype(int)
sx=xx-i;sy=yy-j
interp=np.where(sy<=sx,(1-sx)*ue[i,j]+(sx-sy)*ue[i+1,j]+sy*ue[i+1,j+1],(1-sy)*ue[i,j]+(sy-sx)*ue[i,j+1]+sx*ue[i+1,j+1])
# Interface trace: left-side lower triangle and right-side upper triangle.
jy=np.floor(axis*M).astype(int)
ql=-(ue[32,jy]-ue[31,jy])*M
qr=-c*(ue[33,jy+1]-ue[32,jy+1])*M
out['FEM']={'relative_l2':rel(interp),'flux_max_error':float(max(abs(ql+20/11).max(),abs(qr+20/11).max()))}
rows=[]
for method,seed in [(m,s) for m in ["interface","single"] for s in [11,22,33]]:
 folder=Path(__file__).resolve().parent/f'archive/{method}_c10_seed{seed}'
 checkpoint=torch.load(folder/'checkpoint.pt',map_location='cpu',weights_only=False)
 model=Solver(checkpoint['config']).double().eval();model.load_state_dict(checkpoint['model'])
 with torch.no_grad():u=model(torch.tensor(z,dtype=torch.float64)).numpy().ravel()
 zi=torch.tensor(np.column_stack([np.full(len(axis),.5),axis]),dtype=torch.float64,requires_grad=True)
 flux=[]
 for side,a in [(0,1.),(1,c)]:
  value=model.side(zi,side)
  deriv=torch.autograd.grad(value,zi,torch.ones_like(value),retain_graph=True)[0][:,0]
  flux.append((-a*deriv).detach().numpy())
 met=json.loads((folder/'metrics.json').read_text())
 rows.append({'method':method,'seed':seed,'relative_l2':rel(u),'flux_max_error':float(max(abs(flux[0]+20/11).max(),abs(flux[1]+20/11).max())),'train_seconds':met['train_seconds'],'lbfgs_closure_calls':met['lbfgs_closure_calls']})
for method,label in [('interface','Interface PINN'),('single','Single PINN')]:
 runs=[r for r in rows if r['method']==method]
 out[label]={k:float(np.mean([r[k] for r in runs])) for k in ['relative_l2','flux_max_error','train_seconds']}
 out[label]['runs']=runs
out['training']={'gpu':'NVIDIA A100-PCIE-40GB','precision':'float64','adam_steps':10000,'lbfgs_max_iter':500,'parameters':17154,'network':'2 independent MLPs, each 3 hidden layers of width 64, tanh','interior_points_per_subdomain':2048,'boundary_points_per_edge':256,'interface_points':512}
(Path(__file__).resolve().parent/'comparison.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
print(json.dumps(out,indent=2))
