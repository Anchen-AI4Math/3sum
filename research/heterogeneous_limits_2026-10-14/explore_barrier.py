"""Discover a relaxed ALL-PROFILE lower bound; floating values not a proof."""
import math,json
import numpy as np
from scipy.optimize import differential_evolution,minimize_scalar
from explore_profiles import H,invH
from pathlib import Path
EMIN=1.5*H(1/3)
def f(t):return 0. if t>=1 else (1-t)*math.log2(1-t)

def delta_bound(z,details=False):
    x,b=z
    h=.5+b-x;Q=.5-b-x;v=x-2*b
    if h<=0 or h>=1 or Q<=0 or v<=0 or x<=0:return 0.
    theta=invH(h);tau_min=.5+b+x
    E0=max(EMIN,(v-f(theta))/(2*theta))
    def at(a):
        r=1-a;t=invH(min(Q/r,1))
        pre=max(a*EMIN,a*(v-a*f(theta/a))/(2*theta))
        suf=max(r*EMIN,(v+a-r*f(t))/(2*t))
        return pre+suf
    if theta<tau_min:
        aa=np.linspace(theta,tau_min,31)
        vals=[at(a) for a in aa]
        j=int(np.argmax(vals));lo=aa[max(0,j-1)];hi=aa[min(30,j+1)]
        opt=minimize_scalar(lambda a:-at(a),bounds=(lo,hi),method='bounded')
        E0=max(E0,max(vals),-opt.fun);a=opt.x
    else:a=None
    delta=min(x/(E0-b+x),2*x/(2*E0+x))
    if details:return dict(x=x,b=b,theta=theta,E_lower=E0,a=a,lower_R=2-delta)
    return delta

if __name__=='__main__':
    opt=differential_evolution(lambda z:-delta_bound(z),bounds=[(.001,.499),(-.49,-.000001)],seed=12,popsize=12,maxiter=100,tol=1e-9)
    r=delta_bound(opt.x,True)
    print('FLOAT RELAXATION ONLY',r,flush=True)
    Path(__file__).with_name('barrier_exploration.json').write_text(json.dumps(r,indent=2)+'\n')
