# Written before local runs

These are AI-generated hypotheses, not student sign-off. Do not rewrite them after seeing results.

1. Smooth case: a=1+x, u=sin(pi*x)sin(pi*y); -div(a grad u) includes -pi*cos(pi*x)sin(pi*y). Arithmetic shared faces should give order 2 in the h-weighted interior discrete L2 norm.
2. Layered case: a_L=1, a_R=c, interface x=0.5. Slope_L=2c/(1+c), slope_R=2/(1+c); u is continuous, common +x physical flux is -2c/(1+c). Boundary extrema are 0 and 1. y-independent solution need not be symmetric in x when c!=1.
3. Odd N puts the interface midway between columns; the harmonic face coefficient 2c/(1+c) represents the exact half-edge resistance. Harmonic FDM should reproduce exact nodal values to solver precision. Do not fit orders to round-off errors. Arithmetic averaging gives a wrong resistance for c!=1.
4. Index k=(i-1)(N-1)+(j-1), y-fast C order. At the left interface-adjacent node, east coefficient is -a_H/h^2; other three are -1/h^2; diagonal is (3+a_H)/h^2. Boundary contributions enter RHS positively. The eliminated matrix is SPD by a shared-positive-edge energy sum.
5. Direct-solve backward residual should be near machine precision. Independent CG agreement and a positive small-grid eigenvalue check corroborate the implementation, but do not replace the energy argument.
6. PINN accuracy is not predictable from a small training loss. On independent evaluation points inspect solution, boundary values, flux continuity and bulk PDE residual. Smoke thresholds are engineering checks, not course grading criteria.
7. A global smooth single network has the same derivative from both sides, whereas the exact derivative jumps for c!=1. A two-network model avoids that representational restriction. No superiority claim is assumed.

Every invocation also saves its resolved parameters and predictions before starting its solves.
