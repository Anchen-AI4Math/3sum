"""Numerical discovery of local-energy/report-cost duals; not a proof."""
import numpy as np,math,json
from scipy.optimize import minimize
from affine_search import ROOT,relax,EMIN,f,coeffs,delta_bound
LN4=2*math.log(2)

def minimum_term(b,g):
    b=np.asarray(b);g=np.broadcast_to(g,b.shape);out=np.zeros_like(b)
    mask=b>1e-15
    e=np.maximum(EMIN,np.log2(LN4*g[mask]/b[mask])/2)
    out[mask]=b[mask]*e+g[mask]*np.exp2(-2*e)
    return out

def couple(r,eu,v):
    n=r['n'];rows=r['duals'];A=np.array([2*np.array(s['t'])/n for s in rows])
    rhs=np.array([v+s['j']/n-f(np.array(s['t'])).sum()/n for s in rows])
    lens=np.ones(n)/n
    fun=lambda e:.98*np.exp2(-2*e).mean()
    jac=lambda e:-LN4*.98*np.exp2(-2*e)/n
    E=np.array(r.get('profile',np.full(n,eu)))
    cons=[dict(type='ineq',fun=lambda e:eu-e.mean(),jac=lambda e:-lens),
          dict(type='ineq',fun=lambda e:A@e-rhs,jac=lambda e:A)]
    sol=minimize(fun,E,jac=jac,bounds=[(EMIN,None)]*n,constraints=cons,method='SLSQP',
                 options={'maxiter':400,'ftol':1e-12})
    if not hasattr(sol,'multipliers'):return None
    lam=max(0,float(sol.multipliers[0]));ys=np.maximum(0,sol.multipliers[1:])
    C=ys@A*n;lam=max(lam,float(max(C))+1e-12)
    dual=float(ys@rhs-lam*eu+minimum_term(lam-C,.98).mean())
    return dict(success=bool(sol.success),message=sol.message,kappa_primal=float(sol.fun),kappa_dual=dual,
                lam=lam,rows=[dict(j=s['j'],t=s['t'],y=float(y)) for s,y in zip(rows,ys) if y>1e-12],n=n,
                profile=sol.x.tolist())

if __name__=='__main__':
    output=[]
    for x,h in [(.18239,.29598),(.19,.28),(.19,.29)]:
        cap=.0415;z=h+2*x;eu=x/cap-.5+h;v=1-x-2*h;k=.98*2**(-2*eu)
        for iteration in range(3):
            r=relax([x,x,z,z],k,n=32,maxiter=150)
            achieved=2-delta_bound(*coeffs(r),[x,x,z,z])
            print('energy lower',achieved,flush=True)
            if achieved>2-cap:break
            c=couple(r,eu,v)
            print('coupling',x,h,iteration,'Eup',eu,'old',k,'new',c['kappa_dual'],'success',c['success'],flush=True)
            output.append(dict(x=x,h=h,Eup=eu,old_kappa=k,**c))
            if c['kappa_dual']<=k or c['kappa_dual']>.1:break
            k=c['kappa_dual']
    (ROOT/'coupling_exploration.json').write_text(json.dumps(output,indent=2)+'\n')
