"""Project 2 direction 3. x is coordinate 0; interface is x=1/2."""
import numpy as np
import torch


def exact_np(x, y, case="layered", contrast=10.0):
    if case == "smooth":
        return np.sin(np.pi*x)*np.sin(np.pi*y)
    # a_L=1, a_R=contrast; endpoints u(0)=0, u(1)=1.
    slope = 2*contrast/(1+contrast)
    return np.where(x <= 0.5, slope*x, slope*0.5 + slope/contrast*(x-0.5))


def forcing_np(x, y, case):
    if case == "layered":
        return np.zeros_like(x+y)
    return (2*np.pi**2*(1+x)*np.sin(np.pi*x)*np.sin(np.pi*y)
            - np.pi*np.cos(np.pi*x)*np.sin(np.pi*y))


def exact_torch(z, case, contrast):
    x, y = z[:, :1], z[:, 1:2]
    if case == "smooth":
        return torch.sin(torch.pi*x)*torch.sin(torch.pi*y)
    slope = 2*contrast/(1+contrast)
    return torch.where(x <= 0.5, slope*x, slope*0.5+slope/contrast*(x-0.5))


def coefficients(z, case, contrast, side):
    if case == "smooth":
        return 1+z[:, :1]
    return torch.ones_like(z[:, :1])*(1.0 if side == 0 else contrast)


def forcing_torch(z, case):
    x, y = z[:, :1], z[:, 1:2]
    if case == "layered":
        return torch.zeros_like(x)
    return (2*torch.pi**2*(1+x)*torch.sin(torch.pi*x)*torch.sin(torch.pi*y)
            -torch.pi*torch.cos(torch.pi*x)*torch.sin(torch.pi*y))


def grad(u, z):
    return torch.autograd.grad(u, z, torch.ones_like(u), create_graph=True)[0]


def residual(u, z, case, contrast, side):
    """Strong residual only inside a subdomain; never differentiate a coefficient jump."""
    a = coefficients(z, case, contrast, side)
    flux = a*grad(u, z)
    div = sum(grad(flux[:, k:k+1], z)[:, k:k+1] for k in range(2))
    return -div-forcing_torch(z, case)
