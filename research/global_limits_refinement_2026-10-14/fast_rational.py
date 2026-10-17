"""Rigorous atanh intervals using directed INTEGER rounding at scale 10**30.

18 terms, explicit remainder, no floats. The fixed scale prevents enormous
intermediate rational denominators without sacrificing enclosure.
"""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
import sys
BASE=Path(__file__).resolve().parents[2]/'3sum_certificate_1p960614_v3/3sum_certificate_v3'
sys.path.insert(0,str(BASE))
from exact_interval import Interval,as_iv
from verify_certificate import floor_dec,ceil_dec
SCALE=10**30
TERMS=18

def ceil_div(a,b):return -((-a)//b)

def ln_bounds(x):
    """Scaled integer bounds on ln(x), for rational 1<=x<=2."""
    assert 1<=x<=2
    znum=x.numerator-x.denominator;zden=x.numerator+x.denominator
    pl=znum*SCALE//zden;ph=ceil_div(znum*SCALE,zden)
    sl=pl*pl//SCALE;sh=ceil_div(ph*ph,SCALE)
    low=high=0
    for j in range(TERMS):
        low+=2*pl//(2*j+1);high+=ceil_div(2*ph,2*j+1)
        pl=pl*sl//SCALE;ph=ceil_div(ph*sh,SCALE)
    # Original exact z <= 1/3. A uniform explicit tail is sufficient.
    high+=ceil_div(18*SCALE,8*(2*TERMS+1)*3**(2*TERMS+1))
    return low,high

LN2L,LN2H=ln_bounds(F(2))
LN2=Interval(F(LN2L,SCALE),F(LN2H,SCALE))

@lru_cache(None)
def log2(x):
    x=F(x);assert x>0
    k=0
    while x<1:x*=2;k-=1
    while x>2:x/=2;k+=1
    if x==1:return as_iv(k)
    if x==2:return as_iv(k+1)
    lo,hi=ln_bounds(x)
    return Interval(F(lo*SCALE//LN2H,SCALE)+k,F(ceil_div(hi*SCALE,LN2L),SCALE)+k)

@lru_cache(None)
def entropy_lower(t):
    assert 0<=t<=1
    if t in (0,1):return F(0)
    if t==F(1,2):return F(1)
    return floor_dec((-t*log2(t)-(1-t)*log2(1-t)).lo,16)

@lru_cache(None)
def f_upper(t):
    assert 0<=t<=1
    return F(0) if t==1 else ceil_dec(((1-t)*log2(1-t)).hi,16)
