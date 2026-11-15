# Audit trail — the three claims in table A.2

This folder stores the portions of the AI-assisted work that **changed a claim**
in the report. It is not a conversation dump: for each of the three audits in
table A.2 (`tab:ai_audits`) it records what was asked, what the assistant
returned, what was wrong with it, and the check that decided the matter.

Full session logs are retained by the contributor (Meichen Ding) and can be
produced on request. The file `transcript_excerpts.md` in this folder is the
canonical extract; its SHA-256 is printed in the report (Appendix A, opening
paragraph) and again at the bottom of this file.

---

## Audit 1 — one claim, three different error measures

**Asked.** "In §1 the abstract says arithmetic averaging produces an
$\mathcal{O}(1)$ error in the interface flux. Is that right, and is it the same
statement as the face-conductance error $(1-c)^2/(4c)$?"

**Returned.** Yes, one can speak of an $\mathcal{O}(1)$ error, because the
face conductance is wrong by a factor that does not depend on $h$ — the answer
then used that single factor for the flux, for the nodal error and for the
solution gradient without distinguishing them.

**What was wrong.** Three different quantities were being called "the error":
the *relative face-conductance* error $(1-c)^2/(4c)$ (genuinely
$h$-independent, $=2.025$ at $c=10$); the *nodal* and *midline* interface-flux
errors, which are first order; and the *maximum* interface-flux error over the
square, which is $\mathcal{O}(1)$ for a completely different reason — the exact
Dirichlet trace imposed on $y=0$ and $y=1$.

**What decided it.** A refinement study at $N=31,63,127,255$: the nodal error
falls $1.942\times10^{-2}\to2.383\times10^{-3}$ and the midline flux error
$4.70\times10^{-2}\to5.64\times10^{-3}$ (first order), while the maximum flux
error stays at $0.662$ on every mesh. Evidence: `support/verify/check_interface_order.py`,
Table 5, §2.2–§2.3.

## Audit 2 — a spectral comparison that does not transfer entrywise

**Asked.** "Check the proof of the discrete stability theorem: from
$A_h\succeq a_{\min}A_h^{(1)}$ follows
$A_h^{-1}\le a_{\min}^{-1}(A_h^{(1)})^{-1}$ entrywise, hence
$\|A_h^{-1}\|_\infty\le1/(8a_{\min})$."

**Returned.** The step was flagged as invalid — the Loewner order does not
transfer to the inverse entrywise — and two replacements were offered: a
Courant–Fischer argument for the $L^2$ estimate and an exponential barrier
$\Phi=C_0(e^{\gamma}-e^{\gamma x})$ for the $L^\infty$ estimate.

**What was wrong.** The original step, and the proposed repair: the exponential
barrier was presented as applying to the variable-coefficient operator, where
the barrier identity fails; it is valid for the constant-coefficient operator
only. Both facts were kept: the invalid step is recorded as a counterexample.

**What decided it.** A direct counterexample: $a=1+9\sin^2(\pi x)$, $n=63$,
gives an entrywise ratio of $3.1024>1$, so the entrywise claim is false for
variable coefficients. The conclusion survives with the maximum-principle
barrier: $A_h\varphi=\mathbf{1}$ exactly for
$\varphi=\tfrac12x(1-x)/a_{\min}$ extended by its own boundary values.
Evidence: `support/verify/check_stability.py`, Remark 2.12, Theorem 2.11.

## Audit 3 — symmetry and conservation are not physical correctness

**Asked.** "Our arithmetic operator is symmetric and conserves the shared face
flux, so the interface physics is right. Agree?"

**Returned.** Agreed, and produced a summary table of the operator's algebraic
properties (symmetry, row sums, positivity) as support.

**What was wrong.** The premise is true and the conclusion does not follow: a
matrix can be symmetric, row-sum consistent and locally conservative while its
interface conductance — hence its flux — is wrong by $36\%$.

**What decided it.** Comparing the computed interface flux with the exact
$J_*=-2c/(1+c)=-20/11$: it differs by $0.662$, while the two-sided
reconstructed jump at the nearest pure-material edges is $3.85\times10^{-13}$
and the symmetry defect is exactly zero. Evidence:
`support/verify/check_matrix_evidence.py`, Table 5, §4.3.

## Also rejected

A suggested one-dimensional chain formula for the arithmetic flux,
$J_h^{\text{arith}}=-[(1-h)/(2a_L)+h/((a_L+a_R)/2)+(1-h)/(2a_R)]^{-1}$, was
applied to the two-dimensional benchmark. It is the one-dimensional value; in
two dimensions the exact Dirichlet trace on $y=0,1$ is kept, so the numerical
maximum differs. The report states the one-dimensional formula as a
one-dimensional result only (Remark 2.8).
