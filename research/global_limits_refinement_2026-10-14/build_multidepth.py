"""Discover a complete arbitrary-profile cover using LP dual witnesses."""
from fractions import Fraction as F
from pathlib import Path
import sys,json,math,time
from relaxation import relax,EMIN
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'heterogeneous_limits_2026-10-14'))
from build_barrier import bound
LOWER='1.9574'

def pack(r):
    n=r['n'];rows=[]
    for z in r['duals']:
        t=[F(min(10**6,math.ceil(max(0,x)*10**6)),10**6) for x in z['t']]
        y=F(math.floor(z['y']*10**9),10**9)
        if y:rows.append({'j':z['j'],'y':y,'t':t})
    scale=max([F(0)]+[sum(2*z['y']*z['t'][i] for z in rows) for i in range(n)]) or F(1)
    for z in rows:z['y']/=scale
    # Conservative floating estimate for selection only; verifier recalculates.
    v=r['v'];E=EMIN
    for z in rows:
        ts=list(map(float,z['t']));a=z['j']/n
        fs=sum(0 if t==1 else (1-t)*math.log2(1-t) for t in ts)/n
        mass=sum(ts)/n
        E+=float(z['y'])*(v+a-fs-2*EMIN*mass)
    return E,dict(n=n,rows=[dict(j=z['j'],y=str(z['y']),t=[str(t) for t in z['t']]) for z in rows])

def main():
    cap=2-float(LOWER);counts={'empty':0,'analytic':0,'dual':0,'split':0};start=time.time();seen=0
    def visit(box,depth=0):
        nonlocal seen
        seen+=1;xl,xh,hl,hh=box
        if seen%100==0:print('progress',seen,counts,round(time.time()-start,1),'depth',depth,flush=True)
        if xl+hl>=F(1,2):counts['empty']+=1;return {'kind':'empty'}
        d,w=bound(box)
        if d<cap-1e-8:counts['analytic']+=1;return {'kind':'analytic',**w}
        # On very large rectangles first split; this avoids unhelpful LPs.
        if max(xh-xl,hh-hl)<=F(1,32):
            r=relax(0,0,n=16,box=list(map(float,box)),maxiter=70)
            r['v']=max(0,1-float(xh)-2*float(hh))
            E,w=pack(r)
            d=min(float(xh)/(E+.5-float(hh)),2*float(xh)/(2*E+float(xh)))
            if d<cap-1e-8:counts['dual']+=1;return {'kind':'dual',**w}
        if depth>30:raise RuntimeError(('unclosed',box,d))
        axis=0 if xh-xl>=hh-hl else 1
        mid=(box[2*axis]+box[2*axis+1])/2
        l=list(box);r=list(box);l[2*axis+1]=mid;r[2*axis]=mid
        counts['split']+=1
        out={'axis':axis,'left':visit(l,depth+1),'right':visit(r,depth+1)}
        return out
    tree=visit([F(0),F(1,2),F(0),F(1,2)])
    data={'schema':1,'lower':LOWER,'counts':counts,'tree':tree}
    (ROOT/'multidepth_certificate.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('DISCOVERY',counts,'seconds',time.time()-start,flush=True)

if __name__=='__main__':main()
