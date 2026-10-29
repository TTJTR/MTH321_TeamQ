"""Conservative shared-face five-point assembly, strong Dirichlet elimination."""
import time
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve, cg, eigsh
from .problem import exact_np, forcing_np


def assemble(n, case="layered", contrast=10.0, average="harmonic"):
    if n < 3 or (case == "layered" and n % 2 == 0):
        raise ValueError("Layered benchmark requires odd N >= 3 (interface between columns).")
    h, m = 1/n, n-1
    axis = np.arange(n+1)*h
    x, y = np.meshgrid(axis, axis, indexing="ij")
    a = 1+x if case == "smooth" else np.where(x < .5, 1., contrast)
    boundary = exact_np(x, y, case, contrast)
    rhs = forcing_np(x[1:-1, 1:-1], y[1:-1, 1:-1], case).ravel().copy()
    rows, cols, values = [], [], []
    for i in range(1, n):
        for j in range(1, n):
            row = (i-1)*m+j-1  # C-order, y varies fastest.
            diagonal = 0.
            for di, dj in [(1,0),(-1,0),(0,1),(0,-1)]:
                ii, jj = i+di, j+dj
                aa, ab = a[i,j], a[ii,jj]
                face = 2*aa*ab/(aa+ab) if average == "harmonic" else (aa+ab)/2
                c = face/h**2
                diagonal += c
                if 0 < ii < n and 0 < jj < n:
                    rows.append(row); cols.append((ii-1)*m+jj-1); values.append(-c)
                else:
                    rhs[row] += c*boundary[ii,jj]
            rows.append(row); cols.append(row); values.append(diagonal)
    matrix = coo_matrix((values,(rows,cols)),shape=(m*m,m*m)).tocsr()
    return matrix, rhs, boundary, a


def solve(n, case="layered", contrast=10., average="harmonic", independent=False):
    started = time.perf_counter()
    A, b, U, a = assemble(n, case, contrast, average)
    assembly_seconds = time.perf_counter()-started
    started = time.perf_counter()
    v = spsolve(A,b)
    seconds = time.perf_counter()-started
    U[1:-1,1:-1] = v.reshape(n-1,n-1)
    axis = np.linspace(0,1,n+1)
    x,y = np.meshgrid(axis,axis,indexing="ij")
    err = U-exact_np(x,y,case,contrast)
    # Named discrete L2: h^2 sum over interior nodes.
    norm_a = float(abs(A).sum(axis=1).max())
    backward = np.max(abs(A@v-b))/(norm_a*np.max(abs(v))+np.max(abs(b)))
    skew = A-A.T
    off = A.copy(); off.setdiag(0); off.eliminate_zeros()
    result = dict(n=n,h=1/n,case=case,contrast=contrast,average=average,
                  l2=float(np.linalg.norm(err[1:-1,1:-1])/n),linf=float(abs(err).max()),
                  backward_residual=float(backward),symmetry_relative=float(np.linalg.norm(skew.data)/np.linalg.norm(A.data)),
                  max_offdiagonal=float(off.data.max()),min_diagonal=float(A.diagonal().min()),
                  min_u=float(U.min()),max_u=float(U.max()),nnz=A.nnz,
                  assembly_seconds=assembly_seconds,solve_seconds=seconds)
    if case == "layered":
        left=n//2; aa,ab=a[left,:],a[left+1,:]
        face=2*aa*ab/(aa+ab) if average == "harmonic" else (aa+ab)/2
        q=-face*(U[left+1,:]-U[left,:])*n
        qexact=-2*contrast/(1+contrast)
        # Exclude top/bottom prescribed boundary edges.
        result["interface_flux_error_max"]=float(abs(q[1:-1]-qexact).max())
    if independent:
        second, info = cg(A,b,rtol=1e-12,atol=0,maxiter=10000)
        if info != 0:
            raise RuntimeError(f"Independent CG failed: {info}")
        result["cg_agreement_linf"]=float(abs(second-v).max())
        lo=float(eigsh(A,k=1,which="SA",return_eigenvectors=False)[0])
        hi=float(eigsh(A,k=1,which="LA",return_eigenvectors=False)[0])
        result.update(smallest_eigenvalue=lo,condition_estimate=hi/lo)
    return result,U
