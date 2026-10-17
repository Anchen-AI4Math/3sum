"""Floating search of piecewise-constant expansion profiles; not certification."""
import math,json,time
from pathlib import Path
from functools import lru_cache
import numpy as np
from scipy.optimize import brentq,minimize

def H(t):
    if t<=0 or t>=1:return 0.
    return (-t*math.log(t)-(1-t)*math.log1p(-t))/math.log(2)
def invH(y):
    if y<=0:return 0.
    if y>=1:return .5
    return brentq(lambda t:H(t)-y,1e-16,.5,xtol=1e-14)
@lru_cache(None)
def Ek(c):return c*H(1/c)/2,2*c*H(1/(2*c))-c*H(1/c)-1

class Profile:
    def __init__(self,cs,ws):
        self.cs=np.array(cs);self.ws=np.array(ws);self.ends=np.cumsum(ws)
        self.Es=np.array([Ek(float(c))[0] for c in cs]);self.ks=np.array([Ek(float(c))[1] for c in cs])
        self.E=float(self.Es@self.ws);self.k=float(self.ks@self.ws)
    def query(self,a,v):
        ws=np.minimum(self.ws,np.maximum(0,self.ends-a))
        r=float(ws.sum());target=v+a
        inds=np.argsort(self.cs)
        W=C=T=0.
        for pos,j in enumerate(inds):
            W+=ws[j];C+=ws[j]*self.cs[j];T+=2*ws[j]*self.Es[j]
            nxt=self.cs[inds[pos+1]] if pos+1<len(inds) else math.inf
            if target<=T-C*H(1/nxt)+1e-13:break
        if T<=target or C<=0:return None
        lam=invH((T-target)/C)
        q=W-lam*C;t=q/r
        if t>=.5 or t<=0:return None
        Q=r*H(t)
        phase=min(int(np.searchsorted(self.ends,a,side='right')),len(self.cs)-1)
        cp=self.cs[phase];tp=max(0,1-cp*lam)
        d=math.log2((1-lam)/lam)
        hp=2*self.Es[phase]-cp*H((1-tp)/cp)-d*tp
        deriv=math.log2(1-t)+math.log2((1-t)/t)*(1+hp)/d
        return Q,t,deriv,lam
    def stats(self,v,tau=.65):
        initial=self.query(0,v);last=self.query(tau,v)
        if initial is None or last is None:return None
        cuts=sorted(set([0.,tau]+[float(a) for a in self.ends[:-1] if a<tau]))
        peaks=[]
        for lo,hi in zip(cuts[:-1],cuts[1:]):
            lq=self.query(lo+1e-11,v);hq=self.query(hi-1e-11,v)
            if lq is None or hq is None:return None
            if lq[2]<=0:a=lo
            elif hq[2]>=0:a=hi
            else:a=brentq(lambda a:self.query(a,v)[2],lo+1e-11,hi-1e-11,xtol=1e-12)
            out=self.query(a,v)
            if out is None:return None
            peaks.append((a,out[0]))
        return initial[1],max(q for a,q in peaks),peaks

def ledger(profile,b,S,e,tau=.65):
    stats=profile.stats(S-2*b,tau)
    if stats is None:return None
    theta,Q,peaks=stats;E=profile.E;k=profile.k
    vals=[2*e*E,1+e*(E-b),2-e*S,2-e*(.5+b-H(theta)),2-e*(.5-b-k-Q),
          2-e*(tau-.5-b-k),1.6*e*(E+.5),2+e*(.8-.4*E-2*b),1+e*(.5-b),
          2-e*(E+b),2-2*e*(E+b),1.]
    return dict(exponent=max(vals),costs=vals,theta=theta,Q=Q,peaks=peaks,E=E,kappa=k)

def optimize(cs,ws,b=-.04617,S=.189,e=.21575,tau=.67,maxiter=350,fixed_cs=False):
    K=len(cs)
    x0=np.r_[np.log(cs),ws,b,S,e,tau,1.96]
    def decode(x):return Profile(np.exp(x[:K]),x[K:2*K]),x[-5],x[-4],x[-3],x[-2],x[-1]
    def cons(x):
        p,b,S,e,tau,R=decode(x)
        out=ledger(p,b,S,e,tau)
        if out is None:return np.ones(12)*(-1-(S-2*b))
        return R-np.array(out['costs'])
    cbounds=[(math.log(c),math.log(c)) for c in cs] if fixed_cs else [(math.log(3),math.log(100000))]*K
    res=minimize(lambda x:x[-1],x0,method='SLSQP',bounds=cbounds+[(.001,.999)]*K+[(-.2,-.00001),(.01,.4),(.05,.4),(.55,.72),(1.8,2.0)],
        constraints=[{'type':'eq','fun':lambda x:sum(x[K:2*K])-1},
                     {'type':'ineq','fun':cons},
                     {'type':'ineq','fun':lambda x:np.diff(x[:K])}],
        options={'maxiter':maxiter,'ftol':2e-12})
    p,b,S,e,tau,R=decode(res.x);out=ledger(p,b,S,e,tau)
    return dict(K=K,cs=p.cs.tolist(),ws=p.ws.tolist(),beta=b,saving=S,epsilon=e,tau=tau,
                success=bool(res.success),message=res.message,iterations=res.nit,**(out or {'exponent':10}))

if __name__=='__main__':
    results=[]
    seeds=[([72,252],[.3402,.6598]),([50,140,400],[.18,.25,.57]),
           ([40,90,180,400],[.12,.15,.2,.53]),([35,65,110,180,300,500],[.08,.1,.12,.15,.2,.35])]
    for cs,ws in seeds:
        start=time.time();r=optimize(cs,ws);results.append(r)
        print(json.dumps(r), 'seconds',round(time.time()-start,2),flush=True)
        Path(__file__).with_name('profile_search.json').write_text(json.dumps(results,indent=2)+'\n')
