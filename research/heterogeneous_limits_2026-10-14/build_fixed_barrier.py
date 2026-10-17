"""Discover a complete fixed-profile parameter cover; floating choices only."""
import json,math,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from explore_profiles import Profile,H,invH
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'profile_certificate.json').read_text())
cs=data['expansions'];ws=[F(w) for w in data['weights']]
p=Profile(cs,[float(w) for w in ws]);lower='1.9586103';cap=2-float(lower)
counts={};nodes=0

def G(a,q):
    w=np.minimum(p.ws,np.maximum(0,p.ends-a))
    active=[j for j in np.argsort(p.cs) if w[j]>0]
    W=C=0.
    for i,j in enumerate(active):
        W+=w[j];C+=w[j]*p.cs[j]
        lam=(W-q)/C
        nxt=p.cs[active[i+1]] if i+1<len(active) else math.inf
        if lam>=1/nxt:break
    return sum(w[j]*(2*p.Es[j]-p.cs[j]*H(min(1/p.cs[j],lam))) for j in active)

def up(t):return F(math.ceil((t+2e-13)*1e12),10**12)

def visit(box,depth=0):
    global nodes
    nodes+=1
    xl,xh,hl,hh=box
    if xl+hl>=F(1,2):out={'kind':'empty'}
    elif min(float(xh)/(p.E+.5-float(hh)),2*float(xh)/(2*p.E+float(xh)))<cap-2e-12:out={'kind':'cap'}
    else:
        v=max(0.,1-float(xh)-2*float(hh));th=up(invH(float(hh)))
        out=None
        if G(0,float(th))<v-2e-11:out={'kind':'initial','theta':str(th)}
        else:
            Q=1-float(hl)-2*float(xl)-p.k
            limit=float(hl)+2*float(xl)+p.k
            for a in [F('0.1438'),F('0.1792'),F('0.2438'),F('0.4187'),F('0.4831'),F('0.3036')]:
                if float(a)>limit-1e-11:continue
                ratio=Q/(1-float(a))
                if ratio<0:out={'kind':'negative_query','a':str(a)};break
                if ratio>=1:continue
                t=up(invH(ratio))
                if G(float(a),(1-float(a))*float(t))<v+float(a)-2e-11:
                    out={'kind':'report','a':str(a),'t':str(t)};break
        if out is None:
            if depth>65:raise RuntimeError(('unclosed',box))
            axis=0 if xh-xl>=hh-hl else 1
            mid=(box[2*axis]+box[2*axis+1])/2
            l=list(box);r=list(box);l[2*axis+1]=mid;r[2*axis]=mid
            out={'axis':axis,'left':visit(l,depth+1),'right':visit(r,depth+1)}
    key=out.get('kind','split');counts[key]=counts.get(key,0)+1
    return out

start=time.time();tree=visit([F(0),F(1,2),F(0),F(1,2)])
result={'schema':1,'lower':lower,'expansions':cs,'weights':[str(w) for w in ws],'tree':tree,'counts':counts}
(ROOT/'fixed_profile_barrier.json').write_text(json.dumps(result,indent=1)+'\n')
print(counts,'seconds',time.time()-start,flush=True)
