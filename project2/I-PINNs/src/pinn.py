"""Generic interface-aware PINN baseline, NOT a claimed reproduction of I-PINNs."""
import csv
import random
import time
import numpy as np
import torch
from torch import nn
from .problem import exact_torch, coefficients, residual, grad


class MLP(nn.Module):
    def __init__(self, width, depth):
        super().__init__()
        layers=[]
        for k in range(depth):
            layers += [nn.Linear(2 if k == 0 else width, width), nn.Tanh()]
        layers.append(nn.Linear(width,1))
        self.layers=nn.Sequential(*layers)
        for module in self.modules():
            if isinstance(module,nn.Linear):
                nn.init.xavier_normal_(module.weight)
                nn.init.zeros_(module.bias)

    def forward(self,z):
        return self.layers(2*z-1)


class Solver(nn.Module):
    def __init__(self,cfg):
        super().__init__()
        self.method=cfg["method"]
        self.networks=nn.ModuleList([MLP(cfg["width"],cfg["depth"])
                                    for _ in range(2 if self.method == "interface" else 1)])

    def side(self,z,side):
        return self.networks[side if self.method == "interface" else 0](z)

    def forward(self,z):
        if self.method == "single":
            return self.side(z,0)
        return torch.where(z[:,:1]<=.5,self.side(z,0),self.side(z,1))


def batch(cfg,device,dtype):
    def rand(n):
        return torch.rand(n,2,device=device,dtype=dtype)
    domains=[]; boundaries=[]
    for side in range(2):
        z=rand(cfg["interior_points"])
        # Open subdomains. No strong PDE residual evaluated on the jump.
        z[:,0]=side*.5+.5*(1e-8+(1-2e-8)*z[:,0])
        domains.append(z)
        # Each half has top/bottom edges and its outer vertical edge.
        edges=[]
        for edge in range(3):
            b=rand(cfg["boundary_points"])
            b[:,0]=side*.5+.5*b[:,0]
            if edge < 2: b[:,1]=float(edge)
            else: b[:,0]=float(side)
            edges.append(b)
        boundaries.append(torch.cat(edges))
    interface=rand(cfg["interface_points"]); interface[:,0]=.5
    return domains,boundaries,interface


def loss_terms(model,data,cfg,contrast):
    domains,boundaries,interface=data
    case=cfg["case"]
    zero=domains[0].new_tensor(0.)
    pde=zero; bc=zero
    for side in range(2):
        z=domains[side].detach().requires_grad_(True)
        # Divide by local a to prevent the larger coefficient dominating bulk training.
        r=residual(model.side(z,side),z,case,contrast,side)/coefficients(z,case,contrast,side)
        pde=pde+r.square().mean()/2
        b=boundaries[side]
        bc=bc+(model.side(b,side)-exact_torch(b,case,contrast)).square().mean()/2
    z=interface.detach().requires_grad_(True)
    left,right=model.side(z,0),model.side(z,1)
    continuity=(left-right).square().mean()
    qleft=coefficients(z,case,contrast,0)*grad(left,z)[:,:1]
    qright=coefficients(z,case,contrast,1)*grad(right,z)[:,:1]
    # Same +x normal on both sides. A fixed scale shared by methods and contrasts.
    scale=1. if case == "smooth" else max(1.,contrast)
    flux=((qleft-qright)/scale).square().mean()
    # For a smooth single network [u]=0 automatically; flux penalty is still applied.
    return dict(pde=pde,boundary=bc,continuity=continuity,flux=flux)


def train(cfg,contrast,seed,out):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
    torch.set_num_threads(cfg.get("threads",2))
    device=cfg["device"]
    if device == "auto": device="cuda" if torch.cuda.is_available() else "cpu"
    if device.startswith("cuda") and not torch.cuda.is_available():
        raise RuntimeError("CUDA requested but unavailable; install GPU PyTorch on the server.")
    dtype={"float32":torch.float32,"float64":torch.float64}[cfg["dtype"]]
    model=Solver(cfg).to(device=device,dtype=dtype)
    optimizer=torch.optim.Adam(model.parameters(),lr=cfg["lr"])
    history=[]; weights=cfg["weights"]
    if device.startswith("cuda"): torch.cuda.synchronize()
    started=time.perf_counter()
    def objective(data):
        terms=loss_terms(model,data,cfg,contrast)
        total=sum(weights[k]*v for k,v in terms.items())
        if not torch.isfinite(total): raise FloatingPointError("Non-finite training loss")
        return total,terms
    for step in range(1,cfg["adam_steps"]+1):
        optimizer.zero_grad(set_to_none=True)
        total,terms=objective(batch(cfg,device,dtype))
        total.backward(); optimizer.step()
        if step == 1 or step % cfg["log_every"] == 0 or step == cfg["adam_steps"]:
            row=dict(stage="adam",step=step,total=float(total.detach()),
                     **{k:float(v.detach()) for k,v in terms.items()})
            history.append(row)
            print(f"seed={seed} contrast={contrast:g} step={step} loss={row['total']:.3e}",flush=True)
    # L-BFGS requires a deterministic objective: keep all collocation points fixed.
    lbfgs_calls=0
    if cfg["lbfgs_steps"]:
        fixed=batch(cfg,device,dtype)
        optimizer=torch.optim.LBFGS(model.parameters(),max_iter=cfg["lbfgs_steps"],
                    tolerance_grad=1e-10,tolerance_change=1e-12,line_search_fn="strong_wolfe")
        def closure():
            nonlocal lbfgs_calls
            optimizer.zero_grad(set_to_none=True)
            total,_=objective(fixed); total.backward(); lbfgs_calls+=1
            return total
        optimizer.step(closure)
        total,terms=objective(fixed)
        history.append(dict(stage="lbfgs",step=lbfgs_calls,total=float(total.detach()),
                            **{k:float(v.detach()) for k,v in terms.items()}))
    if device.startswith("cuda"): torch.cuda.synchronize()
    elapsed=time.perf_counter()-started
    torch.save({"model":model.state_dict(),"config":cfg,"contrast":contrast,"seed":seed},out/"checkpoint.pt")
    with (out/"training.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=history[0].keys()); writer.writeheader(); writer.writerows(history)
    result=dict(seed=seed,contrast=contrast,device=device,train_seconds=elapsed,
                parameters=sum(p.numel() for p in model.parameters()),
                adam_steps=cfg["adam_steps"],lbfgs_closure_calls=lbfgs_calls,
                stopping_reason="configured optimizer budget exhausted or L-BFGS internal stop; see validation",
                final_training_losses=history[-1])
    return model,result


def evaluate(model,cfg,contrast):
    p=next(model.parameters())
    n=cfg["eval_intervals"]
    t=torch.linspace(0,1,n+1,device=p.device,dtype=p.dtype)
    x,y=torch.meshgrid(t,t,indexing="ij")
    z=torch.stack([x.ravel(),y.ravel()],dim=1)
    with torch.no_grad():
        u=model(z); exact=exact_torch(z,cfg["case"],contrast); error=u-exact
    # Trapezoidal quadrature, independent of the training samples.
    w=torch.ones_like(x); w[[0,-1],:]*=.5; w[:,[0,-1]]*=.5
    l2=torch.sqrt((w*error.reshape_as(x).square()).sum()/n**2)
    norm=torch.sqrt((w*exact.reshape_as(x).square()).sum()/n**2)
    interface=torch.stack([torch.full_like(t,.5),t],dim=1).requires_grad_(True)
    ul,ur=model.side(interface,0),model.side(interface,1)
    # Physical heat flux q=-a*u_x, with common +x orientation.
    ql=-coefficients(interface,cfg["case"],contrast,0)*grad(ul,interface)[:,:1]
    qr=-coefficients(interface,cfg["case"],contrast,1)*grad(ur,interface)[:,:1]
    qexact=(-2*contrast/(1+contrast) if cfg["case"]=="layered" else -1.5*torch.pi*torch.cos(torch.pi*interface[:,:1])*torch.sin(torch.pi*interface[:,1:2]))
    qscale=abs(qexact) if isinstance(qexact,float) else max(1.,float(qexact.abs().max().detach()))
    # Held-out deterministic shifted grid in each open half, no jump points.
    residual_rms=[]
    for side in range(2):
        a=(torch.arange(16,device=p.device,dtype=p.dtype)+.5)/16
        xx,yy=torch.meshgrid(side*.5+.5*a,a,indexing="ij")
        zz=torch.stack([xx.ravel(),yy.ravel()],1).requires_grad_(True)
        r=residual(model.side(zz,side),zz,cfg["case"],contrast,side)
        residual_rms.append(float(r.square().mean().sqrt().detach()))
    boundary_mask=(z[:,0]==0)|(z[:,0]==1)|(z[:,1]==0)|(z[:,1]==1)
    metrics=dict(l2=float(l2),relative_l2=float(l2/norm),linf=float(error.abs().max()),
                 boundary_linf=float(error[boundary_mask].abs().max()),
                 interface_value_max=float((ul-ur).abs().max().detach()),
                 interface_flux_jump_max=float((ql-qr).abs().max().detach()),
                 interface_flux_relative_max=float((ql-qr).abs().max().detach())/qscale,
                 interface_flux_error_max=float(torch.maximum((ql-qexact).abs(),(qr-qexact).abs()).max().detach()),
                 heldout_pde_rms_left=residual_rms[0],heldout_pde_rms_right=residual_rms[1])
    arrays=dict(x=x.cpu().numpy(),y=y.cpu().numpy(),u=u.reshape_as(x).cpu().numpy(),
                exact=exact.reshape_as(x).cpu().numpy(),error=error.reshape_as(x).cpu().numpy(),
                interface_y=t.cpu().numpy(),flux_left=ql.detach().cpu().numpy().ravel(),flux_right=qr.detach().cpu().numpy().ravel())
    return metrics,arrays
