"""Exploratory cutting-plane relaxation, arbitrary ordered profiles.

Floats discover dual witnesses; they do not establish a lower bound.
"""
from pathlib import Path
import sys,math,json
import numpy as np
from scipy.optimize import linprog,minimize
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'heterogeneous_limits_2026-10-14'))
from explore_profiles import H,invH
EMIN=1.5*H(1/3)

def f(t):
    return np.where(t>=1,0,(1-t)*np.log2(np.maximum(1-t,1e-300)))

def allocation(E,lengths,q):
    """Minimize sum length*(2*E*t+f(t)) at total mass q."""
    inds=np.argsort(E);low=E[inds[0]]
    powers=np.exp2(np.minimum(2*(E-low),900))
    W=C=0.
    for k,j in enumerate(inds):
        W+=lengths[j];C+=lengths[j]*powers[j]
        lam=(W-q)/C
        if k+1==len(inds) or lam>=1/powers[inds[k+1]]:break
    t=np.maximum(0,1-lam*powers)
    return t

def relax(x,h,n=20,box=None,maxiter=45,kappa=0.,warm=None,stop_E=None):
    # Cell averages of E are variables; no monotonicity/order restriction.
    if box is None:xl=xh=x;hl=hh=h
    else:xl,xh,hl,hh=box
    v=max(0,1-xh-2*hh);Q=1-hl-2*xl-kappa;tau=hl+2*xl+kappa
    lengths=np.ones(n)/n
    jobs=[(0,invH(hh))]
    jobs += [(j, (1-j/n)*invH(min(1,Q/(1-j/n))))
             for j in range(1,n) if j/n<=tau+1e-14]
    E=np.full(n,EMIN);rows=[];rhs=[];witness=[];res=None
    if warm:
        for row in warm:
            j=row['j'];t=np.array(row['t'])
            rows.append(2*lengths*t);rhs.append(v+j/n-f(t)@lengths)
            witness.append((j,t))
        res=linprog(lengths,A_ub=-np.array(rows),b_ub=-np.array(rhs),bounds=[(EMIN,None)]*n,method='highs')
        if not res.success:raise RuntimeError(res.message)
        E=res.x
    for it in range(maxiter):
        # Discovery only needs a sufficiently strong dual, not the LP optimum.
        if res is not None and stop_E is not None and res.fun>=stop_E:break
        violated=[]
        for j,q in jobs:
            t=allocation(E[j:],lengths[j:],q)
            full=np.r_[np.zeros(j),t];coeff=2*lengths*full
            bound=v+j/n-f(t)@lengths[j:]
            if coeff@E<bound-1e-9:
                violated.append((coeff,bound,(j,full)))
        if not violated:break
        for c,b,w in violated:rows.append(c);rhs.append(b);witness.append(w)
        res=linprog(lengths,A_ub=-np.array(rows),b_ub=-np.array(rhs),bounds=[(EMIN,None)]*n,method='highs')
        if not res.success:raise RuntimeError(res.message)
        E=res.x
    total=float(E@lengths)
    duals=[]
    if res is not None:
        for y,(j,t) in zip(-res.ineqlin.marginals,witness):
            if y>1e-10:duals.append(dict(y=float(y),j=j,t=t.tolist()))
    d=min(xh/(total+.5-hh),2*xh/(2*total+xh))
    return dict(x=x,h=h,E=total,profile=E.tolist(),delta=d,lower=2-d,iterations=it+1,duals=duals,n=n)

if __name__=='__main__':
    out=[]
    for x,h in [(.171,.329),(.190052,.281403),(.19,.31),(.195,.29)]:
        r=relax(x,h,n=20);out.append(r)
        print({k:v for k,v in r.items() if k not in ('duals','profile')},flush=True)
    opt=minimize(lambda z:-relax(*z,n=20)['delta'],[.19,.29],method='Nelder-Mead',
                 options={'maxiter':130,'xatol':1e-7,'fatol':1e-9})
    r=relax(*opt.x,n=40);out.append(r)
    print('RELAXATION OPTIMUM CANDIDATE',{k:v for k,v in r.items() if k not in ('duals','profile')},flush=True)
    (ROOT/'relaxation_exploration.json').write_text(json.dumps(out,indent=2)+'\n')
