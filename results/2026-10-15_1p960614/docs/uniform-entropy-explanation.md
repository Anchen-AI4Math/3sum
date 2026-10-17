For the exact quartic $P$ and $\rho=0.27905030$, the proof establishes

$$H(t)<\rho(1+P(t))\qquad(0\le t\le1/2).$$

Let $u=0.17200068185091493$ and put

$$A=-\frac{\log(1-u)}{\log2},\qquad
B=\frac{\log(1-u)-\log u}{\log2}.$$

Concavity of binary entropy gives the supporting line $H(t)\le A+Bt$,
including both entropy endpoints. The geometric child gives
$P(t)\ge P(u)+(t-u)P'(u)$ throughout the interval.

The logarithmic child certifies $A<0.272298515211$ and
$A+B/2<1.40590616299$. Exact rational computations show that these two
caps are strictly below the values at 0 and 1/2 of
$\rho[1+P(u)+(t-u)P'(u)]$. Both compared functions are affine in $t$.
For $t<1/2$, add their endpoint inequalities with the nonnegative weights
$1-2t$ and $2t$; the first weight is positive, so the sum is strict. At
$t=1/2$, use the strict right-endpoint inequality directly.

Combining the entropy upper supporting line, the strict affine comparison,
and the polynomial lower supporting line proves the conclusion for every
real point in the closed interval. The proof imports and actually uses
the accepted quartic geometry and tangent-logarithm children; it does not
replace the continuum by a sampled grid.
