"""Floating-point witness discovery only; decisions need verify_global.py."""
import json
import math
from pathlib import Path
from functools import lru_cache
import sys

BASE = Path(__file__).resolve().parents[2] / '3sum_certificate_1p960614_v3/3sum_certificate_v3'
sys.path.insert(0, str(BASE))
from explore import H
from scipy.optimize import minimize_scalar, brentq

@lru_cache(None)
def point(c):
    g=lambda t:c*(H(1/c)-H((1-t)/c))
    opt=minimize_scalar(lambda t:-H(t)/(1+g(t)),bounds=(.0001,.4999),method='bounded',options={'xatol':1e-14})
    rho=-opt.fun
    k=2*c*H(1/(2*c))-c*H(1/c)-1
    a=1-2*rho; A=.5-k-rho
    fun=lambda t:(2*A+a*g(t))/3-(1-2*rho-k-a*H(t))/(2-rho)
    t=brentq(fun,0,.5,xtol=1e-14) if fun(0)*fun(.5)<0 else .25
    return {'rho':rho,'theta':t,'tangent':opt.x}

def bound(lo, hi):
    p = point(hi)
    rho = p['rho'] - 2e-14
    if rho >= .5:
        return 2.0
    k = 2*hi*H(1/(2*hi))-hi*H(1/hi)-1 - 2e-14
    E = lo*H(1/lo)/2 - 2e-14
    t = p['theta']
    g = hi*(H(1/hi)-H((1-t)/hi)) + 2e-14
    a = 1-2*rho
    A = .5-k-rho
    U = max((2*A+a*g)/3, (1-2*rho-k-a*H(t))/(2-rho))
    C = a*E-A
    if C <= 0:
        return -1
    return 2-a*U/(C+(2-rho)*U)

def main():
    target = 1.960613492
    leaves=[]
    pending=[(3,231),(233,2**26-1)]
    while pending:
        lo,hi=pending.pop()
        lb=bound(lo,hi)
        if lb > target+1e-13:
            p=point(hi)
            leaves.append({'lo':lo,'hi':hi,'split':format(p['theta'],'.17f'),
                           'ratio_point':format(p['tangent'],'.17f')})
        elif lo==hi:
            raise ValueError((lo,lb))
        else:
            mid = int(math.sqrt(lo*hi)) if hi>2*lo else (lo+hi)//2
            pending.extend([(lo,mid),(mid+1,hi)])
    leaves.sort(key=lambda x:x['lo'])
    data={'schema':1,'excluded_lower':'1.960613492','tail_start':2**26,
          'retained_c':232,'intervals':leaves}
    out=Path(__file__).with_name('global_certificate.json')
    out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    print('EXPLORATORY WITNESSES, NOT A PROOF:',len(leaves),'integer intervals')
    print('minimum floating bound',min(bound(d['lo'],d['hi']) for d in leaves))

if __name__=='__main__': main()
