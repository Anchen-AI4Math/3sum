#!/usr/bin/env python3
"""Reproducible arithmetic checks for two 3SUM exponent candidates.

Standard-library only. Run: python verify_exponents.py
Optional numerical search: python verify_exponents.py --optimize (needs SciPy).

The interval endpoints and all pass/fail decisions use exact rational arithmetic.
This checks parameter inequalities, NOT a Lean proof or the entire RAM algorithm.
The sharp-tail candidate additionally needs the cost refinement in RESEARCH_NOTE.md.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from functools import lru_cache
from math import comb, log, log1p, log2, ceil


@dataclass(frozen=True)
class Interval:
    lo: F
    hi: F

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError("Reversed interval")

    @staticmethod
    def point(x: F | int) -> Interval:
        return Interval(F(x), F(x))

    def __add__(self, other: Interval | F | int) -> Interval:
        other = as_iv(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self) -> Interval:
        return Interval(-self.hi, -self.lo)

    def __sub__(self, other: Interval | F | int) -> Interval:
        return self + -as_iv(other)

    def __rsub__(self, other: Interval | F | int) -> Interval:
        return as_iv(other) + -self

    def __mul__(self, other: Interval | F | int) -> Interval:
        other = as_iv(other)
        values = (self.lo * other.lo, self.lo * other.hi,
                  self.hi * other.lo, self.hi * other.hi)
        return Interval(min(values), max(values))

    __rmul__ = __mul__

    def reciprocal(self) -> Interval:
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("Interval contains zero")
        return Interval(1 / self.hi, 1 / self.lo)

    def __truediv__(self, other: Interval | F | int) -> Interval:
        return self * as_iv(other).reciprocal()

    def __rtruediv__(self, other: Interval | F | int) -> Interval:
        return as_iv(other) * self.reciprocal()

    def display(self, places: int = 18) -> str:
        def outward(x: F, rounding: str) -> str:
            with localcontext() as ctx:
                ctx.prec = places + 40
                ctx.rounding = rounding
                result = Decimal(x.numerator) / Decimal(x.denominator)
                return format(result.quantize(Decimal(1).scaleb(-places)), 'f')
        return '[' + outward(self.lo, ROUND_FLOOR) + ', ' + outward(self.hi, ROUND_CEILING) + ']'


def as_iv(x: Interval | F | int) -> Interval:
    return x if isinstance(x, Interval) else Interval.point(x)


def reduced_log(x: F, terms: int = 48) -> Interval:
    """For 1 <= x <= 2, use log(x)=2 atanh((x-1)/(x+1)).

    After terms K, remainder is in
    [0, 2*z**(2*K+1)/((2*K+1)*(1-z*z))].
    All z here are nonnegative and at most 1/3.
    """
    if not 1 <= x <= 2:
        raise ValueError("Range reduction failed")
    z = (x - 1) / (x + 1)
    z2 = z*z
    power = z
    partial = F(0)
    for k in range(terms):
        partial += 2 * power / (2*k+1)
        power *= z2
    remainder = 2 * power / ((2*terms+1)*(1-z2))
    return Interval(partial, partial + remainder)


@lru_cache(maxsize=None)
def log_iv(x: F | int) -> Interval:
    x = F(x)
    if x <= 0:
        raise ValueError("Logarithm argument must be positive")
    k = 0
    while x < 1:
        x *= 2
        k -= 1
    while x > 2:
        x /= 2
        k += 1
    return reduced_log(x) + k * reduced_log(F(2))


def entropy_iv(x: F) -> Interval:
    if not 0 < x < 1:
        raise ValueError("Entropy argument must lie in (0,1)")
    return -x * log_iv(x) - (1-x)*log_iv(1-x)


def exponents(c: F, theta: F, sharp: bool) -> tuple[Interval, Interval, Interval]:
    if not c > 10 or not 0 < theta < F(9, 10):
        raise ValueError("Parameters outside theorem range")
    ln4 = log_iv(4)
    old = theta * log_iv((c-1)/9) / ln4
    gamma = ((c*entropy_iv(1/c) - c*entropy_iv((1-theta)/c)
              - theta*log_iv(9))/ln4) if sharp else old
    q = (entropy_iv(theta) + theta*log_iv(9))/ln4
    A = (c*log_iv(10) - c*entropy_iv(1/c)/2 - (c-1)*log_iv(3))/ln4
    return gamma, q, A


def require_positive(label: str, value: Interval | F) -> None:
    value = as_iv(value)
    if value.lo <= 0:
        raise AssertionError(label + ': positivity not certified: ' + value.display())
    print('  PASS ' + label + '; margin ' + value.display())


def check_candidate(name: str, c: F, theta: F, a: F, s: F, target: F,
                    sharp: bool) -> None:
    print('\n' + name)
    print(f'  c={c}, theta={theta}, a={a}, s={s}, b=s/2={s/2}')
    gamma, q, A = exponents(c, theta, sharp)
    R = 1/(A+gamma)
    print('  gamma = ' + gamma.display())
    print('  q     = ' + q.display())
    print('  A     = ' + A.display())
    print('  R     = ' + R.display())
    b = s/2
    require_positive('gamma > s', gamma - s)
    require_positive('1/2-q > s', F(1, 2) - q - s)
    require_positive('1-a*(A+gamma) > 0', 1-a*(A+gamma))
    # Target Exact Triangle exponent is 3 - a*s/2 up to polylog factors.
    tri = 3-a*b
    prime_cost = log_iv(7)/log_iv(2) + F(3, 2)*a
    build_cost = 2+a*(1+b)
    require_positive('prime-selection exponent below triangle exponent', tri-prime_cost)
    require_positive('instance-building exponent below triangle exponent', tri-build_cost)
    cutoff = 2-a*s/4
    require_positive('target strictly exceeds 3SUM cutoff', target-cutoff)
    require_positive('g exponent b < 1/2', F(1, 2)-b)
    print('  Exact Triangle cutoff: ' + as_iv(tri).display())
    print('  3SUM cutoff:          ' + as_iv(cutoff).display())
    print('  3SUM target:          ' + as_iv(target).display())
    print('  NOTE: a positive target gap absorbs logarithmic and n**o(1) factors.')


def tail_sanity() -> None:
    """Exact finite checks; these are a sanity test, not an asymptotic proof."""
    c = 21
    theta = F('0.11202')
    for m in range(1, 101):
        L = c*m
        t = ceil(theta*m)
        bt = comb(L, m-t) * 9**(L-m+t)
        total = sum(comb(L, m-d)*9**(L-m+d) for d in range(t, m+1))
        # total <= beta_t / (1 - 9*m/(L-m+1)), checked over integers.
        if total * (L-m+1-9*m) > bt * (L-m+1):
            raise AssertionError('Tail bound failed')
    print('\nExact finite tail sanity tests: PASS for m=1,...,100.')
    print('Not a proof of the entropy bound or the RAM runtime.')


def optimize() -> None:
    """Exploration only: floating-point local minimization, NOT a global certificate."""
    try:
        from scipy.optimize import minimize_scalar, brentq
    except ImportError as exc:
        raise SystemExit('Optional --optimize needs scipy; basic verification does not.') from exc

    def H(x: float) -> float:
        return -x*log(x)-(1-x)*log1p(-x)

    def values(c: float, t: float, sharp: bool) -> tuple[float, float, float]:
        g = t*log((c-1)/9)/log(4)
        if sharp:
            g = (c*H(1/c)-c*H((1-t)/c)-t*log(9))/log(4)
        q = (H(t)+t*log(9))/log(4)
        A = (c*log(10)-c*H(1/c)/2-(c-1)*log(3))/log(4)
        return g, q, A

    for sharp in (False, True):
        def balance(c: float) -> float:
            return brentq(lambda t: sum(values(c, t, sharp)[:2])-.5,
                          1e-8, .2, xtol=1e-14)
        def objective(c: float) -> float:
            t = balance(c)
            g, q, A = values(c, t, sharp)
            return 2 - min(g, .5-q)/(4*(A+g))
        res = minimize_scalar(objective, bounds=(10.0001, 100), method='bounded',
                              options={'xatol': 1e-9})
        c = float(res.x)
        t = balance(c)
        print(f'\nExploratory numerical optimum ({"sharp" if sharp else "original"}):')
        print(f'  c={c:.12f}, theta={t:.12f}, cutoff={objective(c):.15f}')
        print('  NOT a proof of global optimality or an attained big-O endpoint.')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--optimize', action='store_true')
    args = parser.parse_args()
    print('Exact rational interval certificates (no floating-point decisions).')
    check_candidate('A: existing Corollary 31, retuned parameters',
                    F(22), F('0.11229'), F('0.05405'), F('0.06862'),
                    F('1.999073'), sharp=False)
    check_candidate('B: refined binomial tail, paper-proof candidate',
                    F(21), F('0.11202'), F('0.05665'), F('0.06945'),
                    F('1.999017'), sharp=True)
    tail_sanity()
    if args.optimize:
        optimize()
    print('\nAll arithmetic checks passed. No Lean build was run by this script.')


if __name__ == '__main__':
    main()
