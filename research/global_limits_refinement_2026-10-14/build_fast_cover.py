"""Discover template duals once; adapt them over the complete parameter cover."""
from pathlib import Path
from fractions import Fraction as F
import json,math,time
from relaxation import relax
from build_multidepth import pack,bound
from build_kappa_multidepth import adapt,quick_E
ROOT=Path(__file__).resolve().parent
LOWER='1.958'

def main(filename='kappa_multidepth_fast_certificate.json'):
    cap=2-float(LOWER);start=time.time();templates=[];lps=0
    for x in [.15,.16,.17,.18,.19,.20,.21,.22]:
        for z in [.62,.64,.66,.68,.70]:
            h=z-2*x
            if x+h>=.5:continue
            k=.8*2**(-2*(x/cap-.5+h))
            r=relax(x,h,n=16,maxiter=100,kappa=k)
            templates.append((x,h,r));lps+=1
    print('Templates ready',lps,'seconds',round(time.time()-start,1),flush=True)
    counts={'empty':0,'analytic':0,'dual':0,'split':0};seen=0
    def visit(box,depth=0):
        nonlocal seen,lps
        seen+=1;xl,xh,hl,hh=box;fb=list(map(float,box))
        if seen%200==0:print('cover',seen,counts,'LPs',lps,'seconds',round(time.time()-start,1),'depth',depth,'box',fb,flush=True)
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
            xm=float((xl+xh)/2);hm=float((hl+hh)/2)
            near=sorted(templates,key=lambda z:abs(z[0]-xm)+abs(z[1]-hm))[:6]
            warm=[]
            for _,_,template in near:
                r=adapt(template,fb,float(k));E=quick_E(r)
                warm.extend(r['duals'])
                d=min(float(xh)/(E+.5-float(hh)),2*float(xh)/(2*E+float(xh)))
                if d<cap-3e-7:
                    out=finish(r)
                    if out:return out
            if depth>=22:
                needed=min(fb[1]/cap-.5+fb[3],fb[1]/cap-.5*fb[1])+5e-5
                r=relax(0,0,n=16,box=fb,maxiter=45,kappa=float(k),warm=warm,stop_E=needed);lps+=1
                templates.append((xm,hm,r));out=finish(adapt(r,fb,float(k)))
                if out:return out
        if depth>31:raise RuntimeError(('unclosed',box,d))
        axis=0 if xh-xl>=hh-hl else 1
        mid=(box[2*axis]+box[2*axis+1])/2
        l=list(box);r=list(box);l[2*axis+1]=mid;r[2*axis]=mid
        counts['split']+=1
        return {'axis':axis,'left':visit(l,depth+1),'right':visit(r,depth+1)}
    tree=visit([F(0),F(1,2),F(0),F(1,2)])
    data={'schema':2,'lower':LOWER,'counts':counts,'tree':tree}
    (ROOT/filename).write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('DISCOVERY',counts,'LPs',lps,'seconds',time.time()-start,flush=True)

if __name__=='__main__':main()
