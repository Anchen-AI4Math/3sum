#!/usr/bin/env python3
"""Check analytic and parametric-cost certificates, using exact rationals only.

No Lean, third-party package, floating-point decision, network, or optimizer is
needed. This is NOT a checker for a complete 3SUM machine implementation.
See PROOF.md for the universal analytic and model-barrier arguments.
"""
from __future__ import annotations
import argparse
import copy
import json
from fractions import Fraction as F
from math import comb
from pathlib import Path
from typing import Any
from exact_interval import Interval, as_iv, log_iv, entropy_iv

HALF = F(1, 2)
PIN = '2b639655e07421b9ac743de9090459bab473a7c0'

class CertificateError(ValueError):
    pass

def require(condition: bool, description: str) -> None:
    if not condition:
        raise CertificateError(description)

def rational(x: Any) -> F:
    require(type(x) in (str, int), 'Rationals must be strings or integers, never floats.')
    return F(x)

def entropy(t: F) -> Interval:
    require(0 <= t <= 1, 'Entropy argument outside [0,1].')
    return as_iv(0) if t in (0, 1) else entropy_iv(t) / log_iv(2)

def gamma(c: int, t: F) -> Interval:
    return c * (entropy(F(1, c)) - entropy((1-t)/c))

def exact_coefficient(c: int, j: int) -> Interval:
    if j == 1:
        return log_iv(c-1)/log_iv(2)
    return (1+F((-1)**j, (c-1)**(j-1))) / (j*(j-1)*log_iv(2))

def polyval(coeff: list[F], t: F) -> F:
    return sum((a*t**j for j, a in enumerate(coeff, 1)), F(0))

def derivative(coeff: list[F], t: F) -> F:
    return sum((j*a*t**(j-1) for j, a in enumerate(coeff, 1)), F(0))

def floor_dec(x: F, digits: int) -> F:
    y = x * 10**digits
    return F(y.numerator//y.denominator, 10**digits)

def ceil_dec(x: F, digits: int) -> F:
    return -floor_dec(-x, digits)

def ledger(p: dict[str, F], E: Interval, k: Interval, h: Interval) -> list[tuple[str, Interval]]:
    e, b, s, tau, rho = (p[n] for n in ('epsilon','beta','saving','tau','rho'))
    return [(name, as_iv(v)) for name, v in [
        ('tables', 2*e*E),
        ('encoding', 1+e*(E-b)),
        ('boxes', 2-e*s),
        ('initial_queries', 2-e*(HALF+b-h)),
        ('recursive_reporting', 2-e*(HALF-b-k-rho*(1+s-2*b))),
        ('terminal_reporting', 2-e*(tau-HALF-b-k)),
        ('prime_correlation', e*F(8,5)*(E+HALF)),
        ('auxiliary_correlation', 2+e*(F(4,5)-F(2,5)*E-2*b)),
        ('candidate_listing', 1+e*(HALF-b)),
        ('band_pairs', 2-e*(E+b)),
        ('band_pairs_squared_scale', 2-2*e*(E+b)),
        ('input_read', F(1)),
    ]]

def verify(data: dict[str, Any], verbose: bool = True) -> dict[str, Any]:
    def emit(s: str) -> None:
        if verbose:
            print(s)
    def positive(name: str, x: F | Interval | int) -> None:
        iv = as_iv(x)
        require(iv.lo > 0, name + ': failed, margin ' + iv.display())
        emit('PASS ' + name + ': ' + iv.display())

    require(data['schema_version'] == 1, 'Unsupported certificate version.')
    require(data['base_commit'] == PIN, 'Unexpected source commit.')
    c = data['expansion']
    require(type(c) is int and c >= 3, 'Expansion must be an integer at least 3.')
    p = {k: rational(v) for k,v in data['parameters'].items()}
    pp = data['polynomial']; degree = pp['degree']; denominator = pp['denominator']
    require(type(degree) is int and 2 <= degree <= 32, 'Unsupported polynomial degree.')
    require(type(denominator) is int and denominator > 0, 'Bad polynomial denominator.')
    require(len(pp['numerators']) == degree and all(type(a) is int for a in pp['numerators']),
            'Bad coefficient list.')
    coeff = [F(a, denominator) for a in pp['numerators']]
    u = rational(data['tangent_point'])
    require(0 < u < HALF, 'Tangent point outside the open interval.')
    caps = {k:rational(v) for k,v in data['analytic_caps'].items()}
    emit('\n=== c=' + str(c) + ', degree=' + str(degree) + ': EXACT CERTIFICATE ===')
    emit('Pinned base: ' + data['base_repository'] + '@' + PIN)

    # Universal P <= gamma: PROOF.md derives the positive-coefficient series.
    for j, a in enumerate(coeff, 1):
        require(a > 0, 'Polynomial coefficients must be positive.')
        actual = exact_coefficient(c, j)
        require(a <= actual.lo, f'Coefficient {j} exceeds the true series coefficient.')
    emit(f'PASS all {degree} positive polynomial coefficients lie below gamma coefficients.')
    positive('uniform derivative bound 9-P\'(1/2)', 9-derivative(coeff, HALF))
    emit('By positive coefficients: P is increasing and convex, P<=gamma on [0,1/2].')

    # Supporting-line argument: no grid sampling.
    A = -log_iv(1-u)/log_iv(2)
    B = (log_iv(1-u)-log_iv(u))/log_iv(2)
    rho = p['rho']
    positive('rho>0', rho)
    positive('rho<1/2', HALF-rho)
    margins = []
    for t in (F(0), HALF):
        affine_gap = rho*(1+polyval(coeff,u)+(t-u)*derivative(coeff,u))-(A+B*t)
        positive('uniform entropy affine gap at '+str(t), affine_gap)
        margins.append(affine_gap)
    emit('Conclusion: H(t)<rho*(1+P(t)) for EVERY t in [0,1/2].')

    E = F(c,2)*entropy(F(1,c))
    k = 2*c*entropy(F(1,2*c))-c*entropy(F(1,c))-1
    h = entropy(p['theta0'])
    emit('E = '+E.display(21)); emit('kappa = '+k.display(21)); emit('H(theta0) = '+h.display(21))
    positive('E lower cap', E-caps['E_lower'])
    positive('E upper cap', caps['E_upper']-E)
    positive('kappa lower cap', k-caps['kappa_lower'])
    positive('kappa upper cap', caps['kappa_upper']-k)
    positive('initial entropy upper cap', caps['h0_upper']-h)
    positive('kappa positive', k)

    # All execution-independent scheduling side conditions.
    e,b,s,tau,theta = (p[n] for n in ('epsilon','beta','saving','tau','theta0'))
    v = s-2*b
    for name, val in [('epsilon positive',e),('epsilon<1',1-e),('saving positive',s),
                      ('v positive',v),('theta0 positive',theta),('theta0<1/2',HALF-theta),
                      ('tau positive',tau),('tau<1',1-tau),('bandShift negative',-b)]:
        positive(name,val)
    initial_margin = polyval(coeff,theta)-v
    positive('initial switch P(theta0)>v', initial_margin)
    positive('terminal switch P(1/2)>(v+tau)/(1-tau)',polyval(coeff,HALF)-(v+tau)/(1-tau))
    positive('band exponent positive',e*(E+b))
    positive('band exponent below one',1-e*(E+b))

    # Twelve exact rational, outward-rounded ledger intervals.
    Ebox = Interval(caps['E_lower'],caps['E_upper'])
    kbox = Interval(caps['kappa_lower'],caps['kappa_upper'])
    hbox = Interval(F(0),caps['h0_upper'])
    values = ledger(p,Ebox,kbox,hbox)
    emit('\nALL TWELVE COST CAPS')
    for name,iv in values:
        emit(name+': '+iv.display(21))
        positive('principal beats '+name, p['principal']-iv)
    max_upper = max(iv.hi for _,iv in values)
    positive('target exceeds principal',p['target']-p['principal'])
    emit('MAXIMUM CERTIFIED COST = '+as_iv(max_upper).display(21))

    # Fixed-c idealized-model barrier. This is not a lower bound for 3SUM.
    # The model is relaxed by using favorable lower caps on E,k,rho, exact
    # gamma instead of P, and keeping only the four critical charges.
    barrier_u = rational(data['barrier_ratio_point'])
    require(0 < barrier_u < HALF, 'Invalid barrier ratio witness.')
    point_ratio = entropy(barrier_u)/(1+gamma(c,barrier_u))
    rho0 = floor_dec(point_ratio.lo,15)
    E0 = caps['E_lower']; k0 = caps['kappa_lower']
    t = rational(data['barrier_split'])
    require(0<t<HALF and 0<rho0<HALF and E0>0 and k0>0,'Invalid barrier domain.')
    a = 1-2*rho0; AA = HALF-k0-rho0
    gt = ceil_dec(gamma(c,t).hi,18)
    ht = floor_dec(entropy(t).lo,18)
    # For theta<=t, the switch gives s<=sG. For theta>=t,
    # initial queries give s<=sH. Monotonicity supplies the full continuum.
    sG = (2*AA+a*gt)/3
    sH = (1-2*rho0-k0-a*ht)/(2-rho0)
    U = max(sG,sH)
    C = a*E0-AA
    positive('barrier relaxed denominator intercept',C)
    positive('barrier saving cap',U)
    delta_upper = a*U/(C+(2-rho0)*U)
    Rlower = 2-delta_upper
    positive('model lower bound exceeds declared barrier',Rlower-p['barrier'])
    emit('\nFIXED-c IDEALIZED UNIFORM-ENTROPY MODEL ONLY')
    emit('rho lower witness = '+str(rho0))
    emit('barrier split = '+str(t))
    emit('s_gamma cap = '+as_iv(sG).display(21))
    emit('s_entropy cap = '+as_iv(sH).display(21))
    emit('CERTIFIED MODEL LOWER BOUND = '+as_iv(Rlower).display(21))
    emit('MODEL SANDWICH = ('+str(p['barrier'])+', '+str(p['principal'])+')')

    # Finite identities/smoke tests. Their universal proof is in PROOF.md;
    # finite testing alone is not claimed to prove these statements.
    checks=0
    for micro in range(2,42,2):
        L=c*micro; hh=micro//2
        M=comb(L,micro); V=comb(L,hh); Delta=comb(L-hh,hh); G=comb(micro,hh)
        require(V*Delta == M*G,'Local incidence identity failed.')
        require(Delta<=V and G<2**micro and M>2**micro,'Local finite bounds failed.')
        require(Delta**2 < M*2**micro,'Local degree-square bound failed.')
        checks+=1
    for m in (10,100,10**4,10**8,10**30):
        for micro in (2,6,20,100):
            J=20*(e*m/(20*micro)).__floor__(); mu=J*micro
            require(0<=e*m-mu<20*micro and J%20==0,'Block rounding failed.')
            z=(-b*mu).__floor__()
            require(0<=-b*mu-z<1,'Band rounding failed.')
            checks+=1
    # Exact integer test is equivalent to P(q/r)>=threshold.
    switch_checks=0
    N,D=v.numerator,v.denominator
    for J in (20,40,60):
        for j in range((tau*J).__floor__()+1):
            r=(J-j)*2
            # Exhaust the small q-domain; this is a smoke test, not universal coverage.
            first=None
            for q in range(r//2+1):
                numerator=sum(a*q**i*r**(degree-i) for i,a in enumerate(pp['numerators'],1))
                integer_test = D*(J-j)*numerator >= denominator*(N*J+D*j)*r**degree
                threshold=(v+F(j,J))/(1-F(j,J))
                semantic=polyval(coeff,F(q,r))>=threshold
                require(integer_test==semantic,'Cleared switch equivalence failed.')
                if integer_test and first is None:
                    first=q
                switch_checks+=1
            require(first is not None and first>0,'Switch missing or nonpositive.')
            tfirst=F(first,r)
            threshold=(v+F(j,J))/(1-F(j,J))
            require(polyval(coeff,tfirst)<threshold+F(9,r),'Switch rounding bound failed.')
    emit(f'PASS {checks} local/floor smoke tests and {switch_checks} cleared-switch identity checks.')
    emit('CERTIFICATE PASS: continuous inequalities, all twelve cost caps, model barrier, finite schedules.')
    emit('NO end-to-end modified 3SUM program or machine-runtime proof is claimed by this checker.')
    return {'c':c,'max_upper':max_upper,'model_lower':Rlower,'parameters':p,
            'values':values,'initial_margin':initial_margin,'uniform_margins':margins}

def negative_tests(data: dict[str, Any]) -> None:
    trials=[]
    bad=copy.deepcopy(data);bad['parameters']['rho']='1/10';trials.append(('false entropy ratio',bad))
    bad=copy.deepcopy(data);bad['polynomial']['numerators'][0]*=2;trials.append(('inflated switch coefficient',bad))
    bad=copy.deepcopy(data);bad['parameters']['principal']='1.9';trials.append(('too-small upper exponent',bad))
    bad=copy.deepcopy(data);bad['parameters']['barrier']='1.98';trials.append(('too-large lower barrier',bad))
    for label,bad in trials:
        rejected=False
        try:
            verify(bad,verbose=False)
        except CertificateError:
            rejected=True
        require(rejected,'Negative test wrongly accepted: '+label)
        print('PASS rejection test: '+label)

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('certificates',nargs='*',type=Path)
    ap.add_argument('--self-test',action='store_true',help='Also ensure four forged certificates are rejected.')
    args=ap.parse_args()
    root=Path(__file__).resolve().parent
    paths=args.certificates or [root/'certificates/c256.json',root/'certificates/c232_quartic.json',root/'certificates/c232.json']
    for path in paths:
        data=json.loads(path.read_text(encoding='utf-8'))
        verify(data)
        if args.self_test:
            negative_tests(data)
    print('\nALL REQUESTED CERTIFICATES PASSED.')

if __name__=='__main__':
    try:
        main()
    except (CertificateError,KeyError,ValueError,TypeError,ZeroDivisionError) as exc:
        raise SystemExit('CERTIFICATE REJECTED: '+str(exc)) from exc
