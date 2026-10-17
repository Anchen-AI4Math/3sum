"""Dual witness search with positive-kappa barrier and reusable templates."""
from pathlib import Path
from fractions import Fraction as F
import json,math,time
import numpy as np
from relaxation import relax,invH,EMIN,f
from build_multidepth import pack,bound
ROOT=Path(__file__).resolve().parent
LOWER='1.958'

def adapt(template,box,kappa):
    xl,xh,hl,hh=box;n=template['n'];tau=hl+2*xl+kappa;Q=1-hl-2*xl-kappa
    rows=[]
    for row in template['duals']:
        j=row['j'];a=j/n;r=1-a
        if j and a>tau:continue
        q=invH(hh) if j==0 else r*invH(min(1,Q/r))
        q+=2e-10
        ts=np.array(row['t']);old=ts.sum()/n
        if old<q:
            ts[j:]+=(q-old)/(r-old)*(1-ts[j:])
        elif old>q:
            ts[j:]*=q/old
        rows.append(dict(j=j,y=row['y'],t=ts.tolist()))
    return dict(n=n,duals=rows,v=max(0,1-xh-2*hh))

def quick_E(r):
    n=r['n'];cap=np.zeros(n);E=EMIN
    for row in r['duals']:cap+=2*row['y']*np.array(row['t'])
    scale=max(cap) or 1.
    for row in r['duals']:
        t=np.array(row['t']);y=row['y']/scale
        E+=y*(r['v']+row['j']/n-f(t).sum()/n-2*EMIN*t.sum()/n)
    return E

def main():
    cap=2-float(LOWER);counts={'empty':0,'analytic':0,'dual':0,'split':0};start=time.time();seen=0
    templates=[];lps=0
    def visit(box,depth=0):
        nonlocal seen,lps
        seen+=1;xl,xh,hl,hh=box;fb=list(map(float,box))
        if seen%200==0:print('progress',seen,counts,'LPs',lps,'seconds',round(time.time()-start,1),flush=True)
        if xl+hl>=F(1,2):counts['empty']+=1;return {'kind':'empty'}
        d,w=bound(box)
        if d<cap-1e-8:counts['analytic']+=1;return {'kind':'analytic',**w}
        Eup=float(xh)/cap-.5+float(hh)
        k=F(math.floor(.8*2**(-2*Eup)*10**10),10**10)
        def finish(r):
            E,w=pack(r)
            d=min(float(xh)/(E+.5-float(hh)),2*float(xh)/(2*E+float(xh)))
            if d<cap-2e-8:
                counts['dual']+=1;return {'kind':'dual','kappa':str(k),**w}
        if max(xh-xl,hh-hl)<=F(1,32):
            for template in reversed(templates[-24:]):
                r=adapt(template,fb,float(k));E=quick_E(r)
                d=min(float(xh)/(E+.5-float(hh)),2*float(xh)/(2*E+float(xh)))
                if d<cap-3e-7:
                    out=finish(r)
                    if out is not None:return out
            r=relax(0,0,n=16,box=fb,maxiter=90,kappa=float(k));lps+=1
            templates.append(r);r=adapt(r,fb,float(k))
            out=finish(r)
            if out is not None:return out
        if depth>31:raise RuntimeError(('unclosed',box,d))
        axis=0 if xh-xl>=hh-hl else 1
        mid=(box[2*axis]+box[2*axis+1])/2
        l=list(box);r=list(box);l[2*axis+1]=mid;r[2*axis]=mid
        counts['split']+=1
        return {'axis':axis,'left':visit(l,depth+1),'right':visit(r,depth+1)}
    tree=visit([F(0),F(1,2),F(0),F(1,2)])
    data={'schema':2,'lower':LOWER,'counts':counts,'tree':tree}
    (ROOT/'kappa_multidepth_certificate.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('DISCOVERY',counts,'LPs',lps,'seconds',time.time()-start,flush=True)

if __name__=='__main__':main()
