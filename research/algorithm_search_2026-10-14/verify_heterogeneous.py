"""Exact certificate for a NEW heterogeneous core and CONDITIONAL cost ledger.

Not an end-to-end RAM algorithm verifier. See ALGORITHM_AND_PROOF.txt.
"""
from pathlib import Path
from fractions import Fraction as F
import json,sys,copy,argparse
ROOT=Path(__file__).resolve().parent
BASE=ROOT.parent.parent/'3sum_certificate_1p960614_v3/3sum_certificate_v3'
sys.path.insert(0,str(BASE))
from exact_interval import as_iv,log_iv
from verify_certificate import entropy,gamma,floor_dec,ceil_dec

def require(b,msg):
    if not b:raise ValueError(msg)

def dual(c1,c2,lam):
    require(0<lam<F(1,2),'bad dual point')
    d=(log_iv(1-lam)-log_iv(lam))/log_iv(2)
    hs=[]
    for c in (c1,c2):
        t=max(F(0),1-c*lam)
        hs.append(gamma(c,t)-d*t)
    return d,hs

def weights(split,a):return max(split-a,F(0)),1-max(split,a)

def verify(data,verbose=True):
    require(data['schema']==1,'bad schema')
    c1,c2=data['expansions']
    require(type(c1) is int and type(c2) is int and 3<=c1<c2,'bad c')
    p={k:F(v) for k,v in data['parameters'].items()}
    e,b,S,split,tau,principal,target=(p[k] for k in ['epsilon','beta','saving','split','tau','principal','target'])
    require(0<e<1 and b<0 and S>0 and 0<split<tau<1,'bad parameters')
    v=S-2*b
    cursor=F(0);maxQ=F(0);initial=None;minmargin=None
    for z in data['schedule']:
        lo,hi,lam,qlo,qhi=(F(z[k]) for k in ['lo','hi','lambda','qlo','qhi'])
        require(lo==cursor and lo<hi<=tau,'schedule gap or invalid interval')
        require(not lo<split<hi,'interval crosses type boundary')
        d,hs=dual(c1,c2,lam)
        for a,q in [(lo,qlo),(hi,qhi)]:
            require(0<q<(1-a)/2,'threshold outside half interval')
            w=weights(split,a)
            margin=d*q+w[0]*hs[0]+w[1]*hs[1]-(v+a)
            require(margin.lo>0,'dual box inequality failed')
            minmargin=margin.lo if minmargin is None else min(minmargin,margin.lo)
        # q(a) is the affine interpolant; perspective-entropy tangent is affine.
        tm=(qlo+qhi)/(2-lo-hi)
        A=-log_iv(1-tm)/log_iv(2)
        B=(log_iv(1-tm)-log_iv(tm))/log_iv(2)
        for a,q in [(lo,qlo),(hi,qhi)]:
            bound=(1-a)*A+q*B
            maxQ=max(maxQ,ceil_dec(bound.hi,21))
        if initial is None:initial=qlo
        cursor=hi
    require(cursor==tau and initial is not None,'incomplete schedule')
    E1=F(c1,2)*entropy(F(1,c1));E2=F(c2,2)*entropy(F(1,c2))
    k1=2*c1*entropy(F(1,2*c1))-2*E1-1
    k2=2*c2*entropy(F(1,2*c2))-2*E2-1
    E=split*E1+(1-split)*E2;k=split*k1+(1-split)*k2
    h=entropy(initial)
    vals=[('tables',2*e*E),('encoding',1+e*(E-b)),('boxes',2-e*S),
          ('initial_queries',2-e*(F(1,2)+b-h)),
          ('recursive_reporting',2-e*(F(1,2)-b-k-maxQ)),
          ('terminal_reporting',2-e*(tau-F(1,2)-b-k)),
          ('prime_correlation',e*F(8,5)*(E+F(1,2))),
          ('auxiliary_correlation',2+e*(F(4,5)-F(2,5)*E-2*b)),
          ('candidate_listing',1+e*(F(1,2)-b)),
          ('band_pairs',2-e*(E+b)),('band_pairs_squared_scale',2-2*e*(E+b)),
          ('input_read',F(1))]
    require((e*(E+b)).lo>0 and (e*(E+b)).hi<1,'bad band exponent')
    out={}
    for name,val in vals:
        val=as_iv(val);require(val.hi<principal,'failed ledger: '+name+' '+val.display(24))
        out[name]=val.display(24)
    require(principal<target<F('1.96061349120'),'not a strict improvement')
    result={'status':'EXACT CORE/SCHEDULE + CONDITIONAL LEDGER ONLY',
            'expansions':[c1,c2],'split':str(split),'intervals':len(data['schedule']),
            'initial_theta':str(initial),'query_cap':str(maxQ),
            'minimum_box_margin':as_iv(minmargin).display(24),
            'E':E.display(24),'kappa':k.display(24),'costs':out,
            'principal':str(principal),'target':str(target)}
    if verbose:
        print('PASS entire continuum a in [0,tau]:',len(data['schedule']),'affine schedule pieces.')
        print('PASS all twelve conditional cost caps below',principal,'<',target)
        print(json.dumps(result,indent=2))
        print('No modified complete 3SUM word-RAM runtime proof is claimed.')
    return result

def negative_tests(data):
    trials=[]
    z=copy.deepcopy(data);z['schedule'].pop(0);trials.append(('coverage gap',z))
    z=copy.deepcopy(data);z['schedule'][0]['qlo']='0.0001';trials.append(('undersized query',z))
    z=copy.deepcopy(data);z['parameters']['principal']='1.95';trials.append(('false cost cap',z))
    z=copy.deepcopy(data);z['schedule'][0]['lambda']='0.49';trials.append(('false dual',z))
    for name,z in trials:
        try:verify(z,False)
        except ValueError:print('PASS rejection:',name)
        else:raise ValueError('forged certificate accepted: '+name)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    data=json.loads((ROOT/'heterogeneous_certificate.json').read_text())
    out=verify(data)
    if args.self_test:negative_tests(data)
    (ROOT/'heterogeneous_verification.json').write_text(json.dumps(out,indent=2)+'\n')
