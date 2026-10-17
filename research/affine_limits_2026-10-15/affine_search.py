"""Floating witness discovery in (x,z=h+2x); proof is in verify_affine.py."""
from pathlib import Path
from fractions import Fraction as F
import sys,json,math,time,argparse
import numpy as np
from scipy.optimize import linprog
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent/'global_limits_refinement_2026-10-14'))
from relaxation import EMIN,invH,f,allocation
from build_multidepth import pack

def jobs(box,k,n):
    xl,xh,zl,zh=box
    hh=min(.5,zh-2*xl);tau=zl+k;Q=1-tau
    return [(0,invH(hh))]+[(j,(1-j/n)*invH(min(1,Q/(1-j/n)))) for j in range(1,n) if j/n<=tau]

def adapt(template,box,k):
    n=template['n'];mass=dict(jobs(box,k,n));rows=[]
    for row in template['duals']:
        j=row['j']
        if j not in mass:continue
        q=mass[j]+2e-10;r=1-j/n;t=np.array(row['t']);old=t.sum()/n
        if old<q:t[j:]+=(q-old)/(r-old)*(1-t[j:])
        elif old>q:t[j:]*=q/old
        rows.append(dict(j=j,y=row['y'],t=t.tolist()))
    return dict(n=n,duals=rows,v=1+3*box[0]-2*box[3])

def relax(box,k,n=32,maxiter=120,warm=None,stop=None):
    v=1+3*box[0]-2*box[3];lengths=np.ones(n)/n
    rows=[];rhs=[];witness=[];res=None;E=np.full(n,EMIN)
    for row in warm or []:
        j=row['j'];t=np.array(row['t']);rows.append(2*t/n)
        rhs.append(v+j/n-f(t).sum()/n);witness.append((j,t))
    for it in range(maxiter):
        if rows:
            res=linprog(lengths,A_ub=-np.array(rows),b_ub=-np.array(rhs),bounds=[(EMIN,None)]*n,method='highs')
            if not res.success:raise RuntimeError(res.message)
            E=res.x
            if stop is not None:
                trial=[dict(y=float(y),j=j,t=t.tolist()) for y,(j,t) in zip(-res.ineqlin.marginals,witness) if y>1e-10]
                if stop(dict(n=n,duals=trial,v=v,profile=E.tolist())):break
        added=False
        for j,q in jobs(box,k,n):
            t=np.r_[np.zeros(j),allocation(E[j:],lengths[j:],q)]
            c=2*t/n;b=v+j/n-f(t).sum()/n
            if c@E < b-1e-9:
                rows.append(c);rhs.append(b);witness.append((j,t));added=True
        if not added:break
    duals=[]
    if res is not None:
        for y,(j,t) in zip(-res.ineqlin.marginals,witness):
            if y>1e-10:duals.append(dict(y=float(y),j=j,t=t.tolist()))
    return dict(n=n,duals=duals,v=v,profile=E.tolist())

def coeffs(r):
    n=r['n'];caps=np.zeros(n)
    for row in r['duals']:caps+=2*row['y']*np.array(row['t'])
    scale=max(caps) or 1.;A=EMIN;Y=0.
    for row in r['duals']:
        y=row['y']/scale;t=np.array(row['t']);Y+=y
        A+=y*(row['j']/n-f(t).sum()/n-2*EMIN*t.sum()/n)
    return A,Y

def delta_bound(A,Y,box):
    ds=[[],[]]
    for x in box[:2]:
        for z in box[2:]:
            E=A+Y*(1+3*x-2*z)
            if E+.5+2*x-z<=0 or 2*E+x<=0:return 1.
            ds[0].append(x/(E+.5+2*x-z));ds[1].append(2*x/(2*E+x))
    return min(map(max,ds))

def main(lower='1.95815',n=32):
    cap=2-float(lower);templates=[];start=time.time();lps=0
    for x in [.16,.175,.185,.20,.22]:
        for z in [.62,.65,.67,.70]:
            if not 2*x<z<x+.5:continue
            eu=x/cap-.5+z-2*x;k=.98*2**(-2*eu)
            r=relax([x,x,z,z],k,n=n)
            templates.append((x,z,r));lps+=1
    print('templates',len(templates),'seconds',time.time()-start,flush=True)
    counts=dict(empty=0,base=0,initial=0,dual=0,split=0);seen=0
    def visit(box,depth=0):
        nonlocal seen,lps
        seen+=1;xl,xh,zl,zh=box;fb=list(map(float,box))
        if seen%200==0:print('cover',seen,counts,'LPs',lps,'seconds',round(time.time()-start,1),'depth',depth,flush=True)
        if zh<=2*xl or zl>=xh+F(1,2):counts['empty']+=1;return dict(kind='empty')
        if delta_bound(EMIN,0,fb)<cap-1e-9:counts['base']+=1;return dict(kind='base')
        hh=min(.5,float(zh-2*xl));theta=F(math.ceil(invH(hh)*10**10)+1,10**10)
        theta=min(theta,F(1,2));th=float(theta)
        if th>0 and delta_bound(-float(f(th))/(2*th),1/(2*th),fb)<cap-1e-9:
            counts['initial']+=1;return dict(kind='initial',theta=str(theta))
        eu=min(float(xh)/cap-.5+float(zh-2*xh),float(xh)/cap-float(xh)/2)
        k=F(math.floor(.98*2**(-2*eu)*10**11),10**11)
        def finish(r):
            A,Y=coeffs(r)
            if delta_bound(A,Y,fb)>=cap-4e-8:return None
            _,w=pack(r)
            rr=dict(n=w['n'],duals=[dict(j=s['j'],y=float(F(s['y'])),t=[float(F(t)) for t in s['t']]) for s in w['rows']])
            if delta_bound(*coeffs(rr),fb)>=cap-2e-8:return None
            counts['dual']+=1
            return dict(kind='dual',kappa=str(k),**w)
        if max(xh-xl,zh-zl)<=F(1,32):
            xm=float((xl+xh)/2);zm=float((zl+zh)/2)
            near=sorted(templates,key=lambda a:abs(a[0]-xm)+abs(a[1]-zm))[:5]
            warm=[]
            for _,_,t in near:
                r=adapt(t,fb,float(k));warm.extend(r['duals']);out=finish(r)
                if out:return out
            if depth>=17:
                r=relax(fb,float(k),n=n,maxiter=80,warm=warm);lps+=1
                templates.append((xm,zm,r));out=finish(adapt(r,fb,float(k)))
                if out:return out
        if depth>=32:raise RuntimeError(('unclosed',box))
        axis=0 if xh-xl>=zh-zl else 1;mid=(box[2*axis]+box[2*axis+1])/2
        left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid
        counts['split']+=1
        return dict(axis=axis,left=visit(left,depth+1),right=visit(right,depth+1))
    tree=visit([F(0),F(1,2),F(0),F(1)])
    data=dict(schema=1,lower=lower,kappa_constant='49/50',counts=counts,tree=tree)
    path=ROOT/('affine_'+lower.replace('.','p')+'_certificate.json')
    path.write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('DONE',path.name,counts,'LPs',lps,'seconds',time.time()-start,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lower',default='1.95815');ap.add_argument('--cells',type=int,default=32);a=ap.parse_args();main(a.lower,a.cells)
