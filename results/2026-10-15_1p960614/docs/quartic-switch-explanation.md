For every $0\le t\le1/2$, the expansion-232 quartic satisfies

$$P(t)\le\gamma_{232}(t),\qquad 0<P'(t)<9,\qquad
P(u)+(t-u)P'(u)\le P(t),$$

where $u=0.17200068185091493$. The geometric child supplies the last three
inequalities. The remaining minorant follows by comparing derivatives.

The entropy difference has numerator

$$G(t)=(1-t)\log(1-t)+(231+t)\log(231+t)-231\log231,$$

and therefore $\gamma_{232}(t)=G(t)/\log2$ and
$G'(t)=\log(231+t)-\log(1-t)$. Both logarithmic arguments remain positive
on the entire closed interval.

For $x\ge0$, differentiation of the remainder gives

$$\log(1+x)\ge x-x^2/2+x^3/3-x^4/4.$$

The derivative of the difference is $x^4/(1+x)\ge0$ and the difference
vanishes at zero. The positive logarithmic series gives, for $0\le t<1$,

$$-\log(1-t)\ge t+t^2/2+t^3/3+t^4/4.$$

Apply the first bound at $x=t/231$. After adding these inequalities and
$\log231$, the coefficients through degree three are precisely the
derivative-series coefficients bounded by the accepted logarithmic child.
The fourth-degree remainder is nonnegative because $1-231^{-4}>0$.
Thus $\log2\,P'(t)\le G'(t)$.

The function $G(t)-\log2\,P(t)$ is continuous on the closed interval, has
nonnegative derivative on its interior, and is zero at the left endpoint.
It is nonnegative everywhere on that interval. Dividing by the positive
$\log2$ proves the desired minorant, including both endpoints. The argument
uses the two accepted geometric/logarithmic children through actual theorem
applications, yielding reusable dependency edges.
