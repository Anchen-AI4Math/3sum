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

def dual(cs,lam):
    require(0<lam<F(1,2),'bad dual point')
    d=(log_iv(1-lam)-log_iv(lam))/log_iv(2)
    hs=[]
    for c in cs:
        t=max(F(0),1-c*lam)
        hs.append(gamma(c,t)-d*t)
    return d,hs

def weights(ws,a):
    end=F(0);out=[]
    for w in ws:
        end+=w;out.append(min(w,max(F(0),end-a)))
    return out

def verify(data,verbose=True):
    require(data['schema']==2,'bad schema')
    cs=data['expansions'];ws=[F(w) for w in data['weights']]
    require(len(cs)==len(ws)>0 and all(type(c) is int and c>=3 for c in cs),'bad c')
    require(all(w>0 for w in ws) and sum(ws)==1,'bad weights')
    cuts=[];end=F(0)
    for w in ws[:-1]:end+=w;cuts.append(end)
    p={k:F(v) for k,v in data['parameters'].items()}
    e,b,S,tau,principal,target=(p[k] for k in ['epsilon','beta','saving','tau','principal','target'])
    require(0<e<1 and b<0 and S>0 and 0<tau<1,'bad parameters')
    v=S-2*b
    cursor=F(0);maxQ=F(0);initial=None;minmargin=None
    for z in data['schedule']:
        lo,hi,lam,qlo,qhi=(F(z[k]) for k in ['lo','hi','lambda','qlo','qhi'])
        require(lo==cursor and lo<hi<=tau,'schedule gap or invalid interval')
        require(not any(lo<a<hi for a in cuts),'interval crosses type boundary')
        d,hs=dual(cs,lam)
        for a,q in [(lo,qlo),(hi,qhi)]:
            require(0<q<(1-a)/2,'threshold outside half interval')
            w=weights(ws,a)
            margin=d*q+sum(wi*h for wi,h in zip(w,hs))-(v+a)
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
    Es=[F(c,2)*entropy(F(1,c)) for c in cs]
    ks=[2*c*entropy(F(1,2*c))-2*E-1 for c,E in zip(cs,Es)]
    E=sum(w*Ei for w,Ei in zip(ws,Es));k=sum(w*ki for w,ki in zip(ws,ks))
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
            'expansions':cs,'weights':[str(w) for w in ws],'intervals':len(data['schedule']),
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
    z=copy.deepcopy(data);z['weights'][0]='0';trials.append(('invalid profile',z))
    for name,z in trials:
        try:verify(z,False)
        except ValueError:print('PASS rejection:',name)
        else:raise ValueError('forged certificate accepted: '+name)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    data=json.loads((ROOT/'profile_certificate.json').read_text())
    out=verify(data)
    if args.self_test:negative_tests(data)
    (ROOT/'profile_verification.json').write_text(json.dumps(out,indent=2)+'\n')
