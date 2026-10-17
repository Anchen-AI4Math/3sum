"""Exact rational interval arithmetic for logarithms and binary entropy.

Adapted from the verifier developed in this conversation on 2026-10-13.
Uses a range-reduced atanh series and an explicit rational remainder bound.
No network access and no third-party dependencies are required.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, localcontext, ROUND_FLOOR, ROUND_CEILING
from fractions import Fraction as F
from functools import lru_cache


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


