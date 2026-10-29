"""Independent mathematical checks, not training-loss snapshots."""
import unittest
import numpy as np
import torch
from src.fdm import solve,assemble
from src.problem import residual,exact_torch
from src.pinn import loss_terms, Solver, batch


class ExactModel(torch.nn.Module):
    def side(self,z,side):
        # Evaluate each analytic branch separately to obtain both one-sided traces.
        x=z[:,:1]
        value=(20/11*x if side == 0 else (2*x+9)/11)
        return value+0*x**3+0*z[:,1:2]**3


class Numerics(unittest.TestCase):
    def test_smooth_second_order_and_independent_cg(self):
        rows=[solve(n,"smooth",average="arithmetic",independent=n==15)[0] for n in [15,31,63]]
        for previous,current in zip(rows,rows[1:]):
            order=np.log(previous["l2"]/current["l2"])/np.log(previous["h"]/current["h"])
            self.assertGreater(order,1.95); self.assertLess(order,2.05)
        self.assertLess(rows[0]["cg_agreement_linf"],1e-10)
        self.assertGreater(rows[0]["smallest_eigenvalue"],0)

    def test_layered_resistance_flux_and_matrix(self):
        for c in [1.,10.,100.]:
            row,_=solve(31,"layered",c,"harmonic")
            self.assertLess(row["linf"],1e-10)
            self.assertLess(row["interface_flux_error_max"],1e-9)
            self.assertLess(row["symmetry_relative"],1e-14)
            self.assertLess(row["max_offdiagonal"],0)
            self.assertLess(row["backward_residual"],1e-14)
            self.assertGreaterEqual(row["min_u"],-1e-12)
            self.assertLessEqual(row["max_u"],1+1e-12)
        arithmetic,_=solve(31,"layered",10.,"arithmetic")
        self.assertGreater(arithmetic["linf"],1e-4)

    def test_nonstandard_interface_row(self):
        n=7; A,b,_,_=assemble(n,"layered",10.,"harmonic")
        i,j=3,3; k=(i-1)*(n-1)+j-1
        self.assertAlmostEqual(A[k,k+(n-1)],-n*n*20/11)
        self.assertAlmostEqual(A[k,k],n*n*(3+20/11))
        self.assertEqual(b[k],0.)
        self.assertEqual(A.shape,((n-1)**2,)*2)

    def test_manufactured_forcing_via_autograd(self):
        torch.manual_seed(7)
        z=torch.rand(32,2,dtype=torch.float64,requires_grad=True)
        r=residual(exact_torch(z,"smooth",10),z,"smooth",10,0)
        self.assertLess(float(r.abs().max().detach()),1e-12)

    def test_interface_sign_and_loss(self):
        torch.manual_seed(8)
        domains=[torch.rand(16,2,dtype=torch.float64) for _ in range(2)]
        domains[0][:,0]*=.49; domains[1][:,0]=.51+.49*domains[1][:,0]
        interface=torch.rand(16,2,dtype=torch.float64); interface[:,0]=.5
        cfg=dict(case="layered")
        terms=loss_terms(ExactModel(),(domains,domains,interface),cfg,10.)
        for value in terms.values(): self.assertLess(float(value.detach()),1e-24)

    def test_training_gradient_against_finite_difference(self):
        torch.manual_seed(9)
        cfg=dict(case="layered",method="interface",width=6,depth=2,
                 interior_points=8,boundary_points=4,interface_points=8)
        model=Solver(cfg).double()
        data=batch(cfg,"cpu",torch.float64)
        parameter=next(model.parameters())
        def objective(): return sum(loss_terms(model,data,cfg,10.).values())
        objective().backward()
        analytic=float(parameter.grad[0,0])
        initial=float(parameter[0,0].detach())
        for eps in [1e-4,1e-5,1e-6]:
            with torch.no_grad(): parameter[0,0]=initial+eps
            plus=float(objective().detach())
            with torch.no_grad(): parameter[0,0]=initial-eps
            minus=float(objective().detach())
            with torch.no_grad(): parameter[0,0]=initial
            self.assertAlmostEqual((plus-minus)/(2*eps),analytic,delta=1e-6)


if __name__=="__main__": unittest.main()
