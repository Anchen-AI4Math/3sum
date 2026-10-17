"""Exploratory two-phase heterogeneous-block ledger; no proof decisions."""
import math,json
import numpy as np
from scipy.optimize import brentq,minimize_scalar,differential_evolution
from pathlib import Path

def H(x):
    if x<=0 or x>=1:return 0.
    return (-x*math.log(x)-(1-x)*math.log1p(-x))/math.log(2)
def gamma(c,t):return c*(H(1/c)-H((1-t)/c))
def Ek(c):return c*H(1/c)/2,2*c*H(1/(2*c))-c*H(1/c)-1

def loss(c1,c2,w1,w2,q):
    if c1>c2:c1,c2,w1,w2=c2,c1,w2,w1
    r=w1+w2
    if w1>1e-14 and q<=w1*(1-c1/c2):
        return w1*gamma(c1,q/w1)
    lam=(r-q)/(w1*c1+w2*c2)
    return w1*gamma(c1,max(0,1-c1*lam))+w2*gamma(c2,max(0,1-c2*lam))

def query(c1,c2,split,a,v):
    w1=max(split-a,0);w2=1-max(split,a);r=1-a
    threshold=v+a
    if loss(c1,c2,w1,w2,r/2)<threshold:return None
    q=brentq(lambda q:loss(c1,c2,w1,w2,q)-threshold,0,r/2,xtol=2e-13)
    return r*H(q/r),q/r

def evaluate(z,refine=False):
    c1,c2,split,b,S=z
    tau=.65;v=S-2*b
    if v<=0:return {'exponent':10}
    E1,k1=Ek(c1);E2,k2=Ek(c2)
    E=split*E1+(1-split)*E2;k=split*k1+(1-split)*k2
    aa=sorted(set(np.linspace(0,tau,25).tolist()+[min(split,tau)]))
    qq=[query(c1,c2,split,a,v) for a in aa]
    if any(q is None for q in qq):return {'exponent':10}
    Q=max(q[0] for q in qq);theta=qq[0][1];peak=aa[max(range(len(aa)),key=lambda j:qq[j][0])]
    if refine:
        cuts=sorted(set([0.,min(split,tau),tau]))
        for lo,hi in zip(cuts[:-1],cuts[1:]):
            opt=minimize_scalar(lambda a:-query(c1,c2,split,a,v)[0],bounds=(lo,hi),method='bounded',options={'xatol':1e-12})
            if -opt.fun>Q:Q=-opt.fun;peak=opt.x
    slopes=[2*E,E-b,-S,-(.5+b-H(theta)),-(.5-b-k-Q),-(tau-.5-b-k),
            1.6*(E+.5),.8-.4*E-2*b,.5-b,-(E+b),-2*(E+b),0]
    offsets=[0,1,2,2,2,2,0,2,1,2,2,1]
    # Exact minimax of these twelve affine expressions in epsilon, using floats.
    es=[.001,.5]
    for i in range(12):
        for j in range(i):
            if abs(slopes[i]-slopes[j])>1e-12:
                e=(offsets[j]-offsets[i])/(slopes[i]-slopes[j])
                if 0<e<.5:es.append(e)
    e=min(es,key=lambda e:max(o+e*s for o,s in zip(offsets,slopes)))
    costs=[o+e*s for o,s in zip(offsets,slopes)]
    return dict(exponent=max(costs),epsilon=e,c1=c1,c2=c2,split=split,beta=b,saving=S,
                E=E,kappa=k,theta=theta,query_max=Q,query_peak=peak,costs=costs,tau=tau)

if __name__=='__main__':
    baseline=evaluate([232,232,.45,-.062656016,.193175570],True)
    print('BASELINE',baseline,flush=True)
    results=[]
    for seed in (17,28):
        opt=differential_evolution(lambda z:evaluate(z)['exponent'],
            bounds=[(150,320),(150,320),(.1,.6),(-.09,-.035),(.15,.24)],
            seed=seed,popsize=9,maxiter=120,tol=2e-10,polish=True)
        r=evaluate(opt.x,True);results.append(r);print('CANDIDATE',r,flush=True)
    out={'status':'floating exploratory ledger only','baseline':baseline,'candidates':results}
    Path(__file__).with_name('heterogeneous_exploration.json').write_text(json.dumps(out,indent=2)+'\n')
