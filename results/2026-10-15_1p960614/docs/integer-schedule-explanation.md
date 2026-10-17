Let $J,s,j$ be natural numbers with $J>0$, $s>0$ even, $j<J$, and
$j/J\le13/20$. Put $r=(J-j)s$, $\mu=Js$, $a=j/J$, and
$K=(v+a)/(1-a)$. The proof constructs a least positive integer $q\le r/2$
satisfying the exact cleared comparison and proves

$$K\le P(q/r)<K+9/r,$$

$$S\le2b-a+(1-a)\gamma_{232}(q/r),$$

$$ (1-a)H(q/r)<\rho(1+v)+9\rho/\mu.$$

Positivity makes all denominators nonzero. Since $s$ is even, $r/2$ is an
integer. The rational terminal comparison implies $K<P(1/2)$ for every
allowed level, and the accepted clearing-equivalence child therefore shows
that $r/2$ satisfies the integer predicate. The least natural witness is at
most that bound; the zero predicate is false because its right-hand side is
strictly positive. Every smaller natural number is rejected.

In particular, the preceding point $(q-1)/r$ is below threshold. Both
consecutive points lie in $[0,1/2]$. The quartic child and the mean-value
inequality give a strict increment below $9/r$, proving the enclosure.
The same child supplies $P\le\gamma_{232}$, so multiplying the lower
threshold comparison by $1-a$ gives the box-saving inequality.

The uniform-entropy child bounds $H(q/r)$ by $\rho(1+P(q/r))$.
Multiplying the upper enclosure by the positive $(1-a)\rho$ and using
$r=(1-a)\mu$ gives the last inequality. The allowance $9\rho/\mu$ is
independent of the level. This is a universal proof for all admissible
natural schedules, and uses an exactly decidable integer predicate; no
floating-point or logarithm evaluation is used for choosing $q$.
