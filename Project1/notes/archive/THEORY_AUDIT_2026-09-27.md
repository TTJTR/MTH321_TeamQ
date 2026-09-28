> 历史审查，保留原结论；当前状态见 [report_v2](../../report_v2/README.md)。

# Theory audit — 2026-09-27

Reviewed GitHub `main` in `TTJTR/MTH321_TeamQ`: the two Markdown files in
`Project1/notes/` and, for consistency, `Project1/report/Section2Draft_.tex`.
This is a review; the source files on GitHub were not changed. The numerical
checks cited below are reproducible with `python code/run_all.py` and
`python -m unittest discover -s tests -v` from the local `Project1` directory.

## Overall assessment

The Euler and RK4 updates, stability functions, implicit residual/Jacobian,
step-doubling estimator `(y_f-y_c)/(2^p-1)`, and controller exponent
`1/(p+1)` are correct. The notes are **not ready to insert unchanged into the
report**: several interpretations of accuracy and stability are false, and
the repository's LaTeX draft contains a wrong Topic 5 spectrum.

## Required mathematical corrections

1. **Accepting the fine step does not raise the method's order.**
   [adaptive.md lines 262–264](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_adaptive.md#L262-L264)
   call `y_f` “local extrapolation” and claim one extra order. Two half steps
   retain local error `O(h^(p+1))` and global order `p`, with a smaller error
   constant. For scalar Explicit Euler on `y'=y`, `y_f=(1+h/2)^2y_0`, whose
   one-step error is still `h^2 y_0/4+O(h^3)`. The Richardson-corrected value
   `y_ext=y_f+(y_f-y_c)/(2^p-1)` cancels the leading local term. The actual
   code accepts `y_f`, so describe it as the **fine-step solution**, not as an
   order-raising extrapolated update.

2. **An error controller does not guarantee absolute stability.**
   [adaptive.md lines 239–257](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_adaptive.md#L239-L257)
   claims it must reject until `h` returns inside the stability region.
   Counterexample from Topic 5: at `X=I`, the RHS is zero, so Euler's coarse
   and fine trials agree exactly (`E=0`) for any `h`; nevertheless a normal
   perturbation has Jacobian eigenvalue `-2`, and at `h=2` the Euler
   amplification is `1-2h=-3`, outside its scalar stability interval.
   Replace the guarantee with: “A large coarse/fine discrepancy often causes
   rejection and smaller steps, but local error control alone does not enforce
   a linear or nonlinear stability bound.”

3. **Step-doubling costs three base-method steps per trial, not two.**
   [adaptive.md line 272](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_adaptive.md#L272)
   correctly counts one full and two half steps but calls that “double” cost.
   Against one fixed step it is three times the base step count, before
   rejections or reusable evaluations. For RK4 this implementation uses
   12 RHS evaluations per trial, versus 4 for one fixed RK4 step.

4. **Clarify the implicit-Euler defect convention and its remainder.**
   [schemes.md lines 128–132](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_schemes.md#L128-L132)
   defines the quantity obtained by inserting the exact endpoint into the
   implicit equation. Calling this the *one-step defect* agrees with the
   course convention (Tutorial 3 Supplementary, PDF p. 11); the prior version
   of this audit overstated that terminology objection. Keep it distinct from
   the actual one-step-map error. Define
   `y*=y(t+h)`, `w_h=y(t)+h f(t+h,w_h)` and
   `r*=y*-y(t)-h f(t+h,y*)`. Backward Taylor gives
   `r*=-h^2 y''(xi)/2`; if `y` is `C^3`, it may also be written
   `-h^2 y''(t)/2+O(h^3)`. With a selected root and `hL<1`,
   `||y*-w_h|| <= ||r*||/(1-hL)=O(h^2)`. Do not append an extra `O(h^3)`
   after the exact Lagrange-remainder expression.

5. **A-stability has a limited claim.**
   [schemes.md lines 134–139](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_schemes.md#L134-L139)
   says that Implicit Euler has “unconditional no numerical divergence risk.”
   A-stability says `|R(h lambda)|<=1` for the scalar linear test equation
   with `Re(lambda)<=0`. It does not guarantee that a nonlinear solve finds
   the intended root, that every nonlinear trajectory remains bounded, or
   that a physically growing mode is damped. Topic 5's benchmark has an
   initial positive Jacobian eigenvalue `0.88`, representing real growth of
   its smallest singular value.

6. **The GitHub LaTeX draft's Topic 5 spectrum is wrong.**
   [Section2Draft_.tex lines 540–577](https://github.com/TTJTR/MTH321_TeamQ/blob/371cb73/Project1/report/Section2Draft_.tex#L540-L577)
   claims every eigenvalue lies in `[-26,-2]` and reports stiffness ratio 13.
   For the stated benchmark, the full 9×9 Jacobian spectrum is
   `{-26,-14.16,-8.64,-7.44,-5.76,-4.88,-1.28,-0.72,+0.88}`.
   At an orthogonal equilibrium, six symmetric normal directions have
   eigenvalue `-2` and three skew-symmetric tangent directions have
   eigenvalue `0`. Among initial **negative** modes, the decay-rate spread is
   `26/0.72≈36.1`; the positive mode is physical growth. Therefore
   `0.0769` and `0.1071` are frozen-Jacobian **local estimates**, not
   “rigorous upper bounds for non-divergent integration.” The draft's reference
   to severe “non-normal” frozen-Jacobian interactions is also unsupported:
   this gradient flow's Jacobian is a symmetric Hessian operator at each fixed
   state.

7. **The LaTeX draft's Newton pseudocode tests the wrong candidate residual.**
   [Section2Draft_.tex lines 252–284](https://github.com/TTJTR/MTH321_TeamQ/blob/371cb73/Project1/report/Section2Draft_.tex#L252-L284)
   evaluates `||w-y_n-h f(w+alpha delta)||` in its line search. The first
   term must also be updated: `||w+alpha delta-y_n-h f(w+alpha delta)||`.
   Moreover, `N=floor((T-t0)/h)` can stop before `T`, and the pseudocode
   lacks a final-step clip or a controlled retry after Newton failure.
   Synchronize this draft with the more recent Section 2 PDF or with the
   implemented solver before using it in the report.

## Precision and completeness edits

- [schemes.md lines 16 and 34](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_schemes.md#L16-L34):
  for general `t0`, write `N=(T-t0)/h` and `exp(L(T-t0))`. Interpret the
  Grönwall expression by continuity when `L=0`.
- [schemes.md lines 88–97](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_schemes.md#L88-L97):
  the `1/16` error ratio and slope 4 are **asymptotic expectations**, not
  guarantees for each finite mesh. Local RK4 errors require an exact starting
  state in the one-step statement. The local benchmark data give a fine-grid
  fitted slope of about `3.927`, with irregular coarse-grid ratios.
- [adaptive.md lines 21–23](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_adaptive.md#L21-L23)
  promises an embedded-pair derivation but provides only step doubling.
  Remove that promise or add a real embedded-pair method and derivation.
- [adaptive.md lines 39–43 and 171–175](https://github.com/TTJTR/MTH321_TeamQ/blob/11fd12a/Project1/notes/theory_section2_adaptive.md#L39-L43):
  varying time scales are a motivation for adaptivity, not a prerequisite.
  `E<=1` controls an **estimated local error**, not a rigorous guarantee
  that every actual component error lies below tolerance. In practical
  integration the reference flow starts at the current numerical state
  `y_n`, which need not equal the original exact trajectory at `t_n`.
- [Section2Draft_.tex lines 654–665](https://github.com/TTJTR/MTH321_TeamQ/blob/371cb73/Project1/report/Section2Draft_.tex#L654-L665):
  the linear-multistep root-condition and Lax–Dahlquist claim is overbroad
  for a general nonlinear one-step solver. State convergence using the
  one-step-map Lipschitz bound and local truncation error already proved.
- [Section2Draft_.tex lines 490 and 574](https://github.com/TTJTR/MTH321_TeamQ/blob/371cb73/Project1/report/Section2Draft_.tex#L490-L574)
  reference `fig:stability_overlay`, but the draft currently defines no such
  figure label. Insert the generated stability figure or revise the reference.

The `notes/` files alone do not establish Topic 5's full finite-time matrix
solution, Lyapunov identity, orthogonal-equilibrium neutral directions, and
rank-deficient limit. Those must appear in the final report even if the notes
remain a background derivation aid.
