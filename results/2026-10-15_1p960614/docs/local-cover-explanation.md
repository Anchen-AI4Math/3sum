For natural $c\ge3$ and $h>0$, put $s=2h$, $L=cs$, $M=\binom Ls$,
$V=\binom Lh$, $\Delta=\binom{L-h}h$, and $G=\binom sh$. The proof establishes

$$V\Delta=MG,\qquad \Delta\le V,\qquad G<2^s<M,\qquad \Delta^2<M2^s.$$

The binomial multiplication identity counts the same pairs of disjoint
$h$-subsets by first choosing the left endpoint, or by choosing their union
and then its left half. Monotonicity in the ground-set size gives
$\Delta\le V$, and a binomial coefficient is strictly below the sum of all
coefficients in its positive row, giving $G<2^s$.

Choosing one coordinate from each of $s$ disjoint blocks of size $c$ is an
injection from the $c^s$ functions to the $s$-subsets of their union. Therefore
$c^s\le M$. Since $c>2$ and $s>0$, $2^s<c^s\le M$. Finally,

$$\Delta^2\le V\Delta=MG<M2^s.$$

The finite injection and binomial-count argument adapt the pinned upstream
LocalCoverBounds and LayerCounts sources, retaining their attribution.
They work for general expansion and cover $c=232$ without asserting the
remaining global program or its runtime.
