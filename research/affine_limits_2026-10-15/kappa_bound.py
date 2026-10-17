"""Exact local kappa-energy inequality, valid for every real c >= 3.

Only standard-library rational interval arithmetic. Finite cover [3,16]
and an analytic tail, not a finite sample of expansion factors.
"""
from pathlib import Path
from fractions import Fraction as F
import sys,json
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'global_limits_refinement_2026-10-14'))
from fast_rational import log2,LN2,as_iv

CONSTANT=F(49,50)

def A(c):
    return -(c-1)*log2(1-1/c)  # A(c)/ln(2)

def prove(constant=CONSTANT):
    # E increases, k decreases (positive inverse-power series).
    c=F(3);count=0;worst=None
    while c<16:
        d=min(F(16),F((c.numerator*10003*10**6)//(c.denominator*10000),10**6))
        assert d>c
        e2=(log2(c)+A(c)).lo
        k=(A(2*d)-A(d)).lo
        assert k>0
        margin=log2(k/constant).lo+e2
        assert margin>0, (c,d,margin)
        worst=margin if worst is None else min(worst,margin)
        c=d;count+=1
    # u=1/c <= 1/16. B=1-A <= u/2+u^2/[6(1-u)].
    # 4*(A(2c)-A(c))/u >= 1+s, s=u/2+7*u^2/24.
    # ln(1+s)>=s-s^2/2, so ln(product*4 ln2)>=1-eta.
    umax=F(1,16)
    coeff=F(7,24)-1/(6*(1-umax))-(F(1,2)+F(7,24)*umax)**2/2
    assert coeff<0
    eta=-coeff*umax**2
    # ln(4*ln(2)*constant) < 1-eta, with monotone upper enclosure.
    tail_log=(log2(4*LN2.hi*constant)*LN2).hi
    assert tail_log<1-eta
    return {'constant':str(constant),'real_c_domain':'[3,infinity)',
            'finite_cover_intervals':count,'finite_min_log2_margin':as_iv(worst).display(20),
            'tail_eta':str(eta),'tail_natural_log_margin':as_iv(1-eta-tail_log).display(20),
            'status':'PASS: k_c >= constant * 4^(-E_c), including analytic infinite tail'}

if __name__=='__main__':
    result=prove()
    print(json.dumps(result,indent=2))
    try:prove(F(99,100))
    except AssertionError:result['inflated_constant_rejected']=True
    else:raise AssertionError('accepted false constant')
    (ROOT/'kappa_bound_verification.json').write_text(json.dumps(result,indent=2)+'\n')
