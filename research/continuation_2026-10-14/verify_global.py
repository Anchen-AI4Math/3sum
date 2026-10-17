"""Exact rational verifier for homogeneous integer-c model exclusion.

No float/optimizer/network decisions. Universal argument: GLOBAL_PROOF.txt.
This does NOT verify an end-to-end 3SUM algorithm or its machine runtime.
"""
from fractions import Fraction as F
from pathlib import Path
import argparse
import copy
import json
import sys

ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent/'3sum_certificate_1p960614_v3/3sum_certificate_v3'
sys.path.insert(0,str(BASE))
from verify_certificate import entropy, gamma, floor_dec, ceil_dec, verify as verify_v3
from exact_interval import as_iv

def require(b,msg):
    if not b: raise ValueError(msg)

def lower_for_interval(d):
    lo,hi=d['lo'],d['hi']
    require(type(lo) is int and type(hi) is int and 3<=lo<=hi,'bad interval')
    t,u=F(d['split']),F(d['ratio_point'])
    require(0<t<F(1,2) and 0<u<F(1,2),'bad witnesses')
    E=floor_dec((F(lo,2)*entropy(F(1,lo))).lo,21)
    k=floor_dec((2*hi*entropy(F(1,2*hi))-hi*entropy(F(1,hi))-1).lo,21)
    rho=floor_dec((entropy(u)/(1+gamma(hi,u))).lo,21)
    require(E>0 and k>0 and rho>0,'bad analytic caps')
    # E increases, k decreases, gamma increases with c; see proof.
    if rho>=F(1,2):
        return F(2)
    a=1-2*rho
    A=F(1,2)-k-rho
    gt=ceil_dec(gamma(hi,t).hi,21)
    ht=floor_dec(entropy(t).lo,21)
    U=max((2*A+a*gt)/3,(1-2*rho-k-a*ht)/(2-rho))
    if U<=0:
        return F(2)
    C=a*E-A
    require(C>0,'nonpositive denominator intercept')
    return 2-a*U/(C+(2-rho)*U)

def verify(data,verbose=True):
    require(data['schema']==1,'wrong schema')
    require(data['retained_c']==232,'wrong retained c')
    start=data['tail_start']
    require(type(start) is int and start==2**26,'wrong tail threshold')
    target=F(data['excluded_lower'])
    require(F('1.960613492')<=target<2,'wrong exclusion target')
    # x=(2-R)/e<1/2 from the initial cost and b<0; e<1/E from encoding.
    # E_c >= log2(c)/2 >= 13 for c >= 2^26, hence delta < 1/26.
    tail_lower=2-F(1,26)
    require(tail_lower>target,'tail bound too weak')
    cursor=3
    answers=[]
    for d in data['intervals']:
        if cursor==232: cursor=233
        require(d['lo']==cursor,'gap, overlap, or unsorted intervals')
        require(not d['lo']<=232<=d['hi'],'interval covers retained c')
        require(d['hi']<start,'interval overlaps tail')
        lb=lower_for_interval(d)
        require(lb>target,'failed interval bound: '+str(d))
        answers.append({'lo':d['lo'],'hi':d['hi'],'lower':as_iv(lb).display(24)})
        cursor=d['hi']+1
    require(cursor==start,'incomplete integer cover')
    old=json.loads((BASE/'certificates/c232.json').read_text(encoding='utf-8'))
    incumbent=verify_v3(old,verbose=False)
    require(incumbent['max_upper']<target,'incumbent does not beat exclusions')
    require(incumbent['model_lower']>F('1.96061349120'),'bad global lower')
    p=incumbent['parameters']
    u=F(old['barrier_ratio_point'])
    v=p['saving']-2*p['beta']
    g=gamma(232,u)
    depth=(g-v)/(1+g)
    require(depth.lo>0 and depth.hi<p['tau'],'critical depth not visited')
    forced_entropy=(1+v)*entropy(u)/(1+g)
    entropy_gap=p['rho']*(1+v)-forced_entropy
    require(entropy_gap.lo>0 and entropy_gap.hi<F('0.000000001'),
            'unexpected depthwise entropy gap')
    result={'interval_count':len(answers),'tail_start':start,
            'tail_lower':as_iv(tail_lower).display(24),
            'excluded_lower':str(target),
            'incumbent_upper':as_iv(incumbent['max_upper']).display(24),
            'global_lower':as_iv(incumbent['model_lower']).display(24),
            'fixed_parameters_critical_depth':depth.display(24),
            'depthwise_entropy_improvement_cap':entropy_gap.display(24),
            'recursive_exponent_improvement_cap':(p['epsilon']*entropy_gap).display(24),
            'intervals':answers}
    if verbose:
        print('PASS exact cover:',len(answers),'integer intervals plus infinite tail; only c=232 retained.')
        print('PASS every excluded integer c has model cost >',target)
        print('PASS c=232 feasible cost:',result['incumbent_upper'])
        print('PASS global integer-c model lower:',result['global_lower'])
        print('PASS tail c>=2^26:',result['tail_lower'])
        print('PASS fixed-parameter exact-depth obstruction:',result['fixed_parameters_critical_depth'])
        print('Recursive exponent gain from sharper entropy alone <',
              result['recursive_exponent_improvement_cap'])
        print('MODEL ONLY: no end-to-end 3SUM runtime or mixed-c claim.')
    return result

def negative_tests(data):
    bad=copy.deepcopy(data);bad['intervals'].pop(0)
    bad2=copy.deepcopy(data);bad2['intervals'][0]['ratio_point']='0.0000001'
    bad3=copy.deepcopy(data);bad3['excluded_lower']='1.99'
    bad4=copy.deepcopy(data);bad4['tail_start']=2**25
    for label,trial in [('missing coverage',bad),('false ratio witness',bad2),
                        ('false lower target',bad3),('invalid tail',bad4)]:
        try: verify(trial,verbose=False)
        except (ValueError,ZeroDivisionError): print('PASS rejection:',label)
        else: raise ValueError('forged certificate accepted: '+label)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    data=json.loads((ROOT/'global_certificate.json').read_text(encoding='utf-8'))
    result=verify(data)
    if args.self_test: negative_tests(data)
    (ROOT/'global_verification.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print('ALL GLOBAL MODEL CHECKS PASSED.')

if __name__=='__main__': main()
