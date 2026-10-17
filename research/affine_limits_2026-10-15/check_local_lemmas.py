"""Independent arithmetic/regression checks; global lemmas are proved in PROOF.txt."""
from fractions import Fraction as F
from pathlib import Path
import json,random
from coupled_exact import min_term,EMIN
from fast_rational import log2,LN2
from verify_certificate import entropy,gamma
from exact_interval import log_iv,as_iv
from parametric_exact import summarize
ROOT=Path(__file__).resolve().parent

def main():
    cases=0;worst=None
    for c in [3,4,7,16,31,64,334,1000]:
        E=c*entropy(F(1,c))/2;k=2*c*entropy(F(1,2*c))-2*E-1
        for t in [F(1,100),F(1,10),F(1,4),F(1,2),F(3,5),F(3,4),F(9,10),F(99,100)]:
            ft=(1-t)*log_iv(1-t)/log_iv(2)
            margin=(2*E*t+ft-gamma(c,t)-(1-t)*min(2*t,F(1))*k).lo
            # At t=1/2 the coefficient comparison is equality for every c.
            if t==F(1,2):
                whole=2*E*t+ft-gamma(c,t)-(1-t)*k
                assert whole.lo<=0<=whole.hi
            else:assert margin>0
            cases+=1
    rng=random.Random(20261015);mins=0
    for _ in range(80):
        b=F(rng.randint(1,10000),100000);g=F(rng.randint(1,10000),10000)
        # Independent high-precision evaluation of the unrestricted minimum.
        l2=log_iv(2)
        inner=2*l2*g/b
        ref_low=log_iv(inner.lo)/l2
        ref_high=log_iv(inner.hi)/l2
        ref=(ref_low+1/l2)*b/2
        free_fast=(log2(2*LN2.lo*g/b).lo+1/LN2.hi)*b/2
        assert free_fast<=ref.lo
        assert b*EMIN<=min_term(b,g)<=max(b*EMIN,ref.lo)
        mins+=1
    mixed=dict(n=1,rows=[dict(j=0,y='1',t=[['99/100'],['1/10'],['99/100'],['1/10']])])
    try:summarize(mixed,[F(1,10),F(1,5),F(1,2),F(3,5)],F(1,100))
    except ValueError as exc:assert 'interpolation' in str(exc)
    else:raise AssertionError('accepted mixed entropy/mass branches')
    result=dict(entropy_kappa_relation_checks=cases,minimum_formula_checks=mins,mixed_branch_interpolation_rejected=True,
                status='PASS: independent arithmetic checks; not a replacement for the universal proof')
    (ROOT/'local_checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
