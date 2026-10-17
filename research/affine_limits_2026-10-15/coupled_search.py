"""Discover a full affine cover with repeated local kappa-energy dual boosts."""
from pathlib import Path
from fractions import Fraction as F
import json,math,time,argparse
import numpy as np
from affine_search import ROOT,relax,adapt,coeffs,delta_bound,EMIN,f,invH,pack
from coupling_explore import couple,minimum_term
from coupled_exact import boost_bound,energy_bound

def raw_coeffs(r):
    n=r['n'];C=np.zeros(n);G=np.zeros(n);B=Y=0.
    for row in r['duals']:
        y=row['y'];t=np.array(row['t']);C+=2*y*t;G+=1.6*y*t*(1-t)
        B+=y*(row['j']/n-f(t).sum()/n);Y+=y
    return B,Y,C,G

def energy_float(r,box):
    B,Y,C,G=raw_coeffs(r);scale=max(C) or 1.;B/=scale;Y/=scale;C/=scale;G/=scale
    best=(delta_bound(B+EMIN*(1-C.mean()),Y,box),1.,False)
    for s in [.9995,.999,.998,.997,.995,.99]:
        M=minimum_term(np.maximum(0,1-s*C),s*G).mean()
        cand=(delta_bound(s*B+M,s*Y,box),s,True)
        if cand[0]<best[0]:best=cand
    return best

def coupling_float(r,box,cap):
    B,Y,C,_=raw_coeffs(r);lam=max(r['lam'],max(C)+1e-11)
    M=minimum_term(lam-C,.98).mean()
    vals=[B+Y*(1+3*x-2*z)-lam*(x/cap-.5+z-2*x)+M for x in box[:2] for z in box[2:]]
    return min(vals),lam

def pack_boost(r,lam):
    rows=[]
    for row in r['duals']:
        y=F(math.floor(row['y']*10**12),10**12)
        if y==0:continue
        ts=[F(min(10**6,math.ceil(max(0,t)*10**6)),10**6) for t in row['t']]
        rows.append(dict(j=row['j'],y=str(y),t=list(map(str,ts))))
    n=r['n'];maxc=max(sum(2*F(s['y'])*F(s['t'][i]) for s in rows) for i in range(n))
    ll=max(F(math.ceil(lam*10**12),10**12),maxc+F(1,10**12))
    return dict(n=n,rows=rows,**{'lambda':str(ll)})

def main(lower='1.95845',n=32):
    cap=2-float(lower);fcap=2-F(lower);start=time.time();energies=[];couplings=[];lps=0
    points=[(.17,.65),(.18,.65),(.1825,.66),(.19,.66),(.19,.67),(.20,.67),(.21,.68)]
    for x,z in points:
        eu=x/cap-.5+z-2*x;k=.98*2**(-2*eu)
        for it in range(3):
            r=relax([x,x,z,z],k,n=n,maxiter=150);lps+=1;energies.append((x,z,r))
            if energy_float(r,[x,x,z,z])[0]<cap-2e-6:break
            c=couple(r,eu,1+3*x-2*z)
            if c is None or c['kappa_dual']<=k+1e-6 or c['kappa_dual']>.1:break
            cr=dict(n=n,duals=c['rows'],lam=c['lam']);couplings.append((x,z,cr));k=c['kappa_dual']-1e-8
    print('templates',len(energies),len(couplings),'seconds',round(time.time()-start,1),flush=True)
    counts=dict(empty=0,base=0,initial=0,dual=0,split=0);seen=0;boostcount=0
    journal=ROOT/('coupled_'+lower.replace('.','p')+'_leaves.jsonl')
    cache={}
    if journal.exists():
        for line in journal.read_text().splitlines():
            entry=json.loads(line);cache[tuple(entry['box'])]=entry['node']
    def visit(box,depth=0):
        nonlocal seen
        key=tuple(map(str,box))
        if key in cache:
            node=cache[key];counts[node['kind']]+=1;seen+=1;return node
        node=visit_raw(box,depth)
        if 'axis' not in node:
            with journal.open('a') as out:out.write(json.dumps(dict(box=key,node=node),separators=(',',':'))+'\n')
        return node
    def visit_raw(box,depth=0):
        nonlocal seen,lps,boostcount
        seen+=1;xl,xh,zl,zh=box;fb=list(map(float,box));xm=float((xl+xh)/2);zm=float((zl+zh)/2)
        if seen%100==0:print('cover',seen,counts,'boosts',boostcount,'LPs',lps,'seconds',round(time.time()-start,1),'depth',depth,'box',fb,flush=True)
        if zh<=2*xl or zl>=xh+F(1,2):counts['empty']+=1;return dict(kind='empty')
        if delta_bound(EMIN,0,fb)<cap-1e-9:counts['base']+=1;return dict(kind='base')
        hh=min(.5,float(zh-2*xl));th=min(F(1,2),F(math.ceil(invH(hh)*10**10)+1,10**10));t=float(th)
        if t>0 and delta_bound(-float(f(t))/(2*t),1/(2*t),fb)<cap-1e-9:
            counts['initial']+=1;return dict(kind='initial',theta=str(th))
        eu=min(float(xh)/cap-.5+float(zh-2*xh),float(xh)/cap-float(xh)/2)
        basek=F(math.floor(.98*2**(-2*eu)*10**11),10**11);k=basek;boosts=[]
        def finish(r):
            d,s,corr=energy_float(r,fb)
            if d>=cap-5e-8:return None
            _,w=pack(r)
            if corr:
                for row in w['rows']:row['y']=str(F(row['y'])*F(str(s)))
            w['gamma_correction']=corr
            if energy_bound(w,box,k)>=fcap-F(1,10**9):return None
            counts['dual']+=1
            return dict(kind='dual',kappa=str(basek),boosts=boosts.copy(),**w)
        if max(xh-xl,zh-zl)<=F(1,32):
            for phase in range(4):
                near=sorted(energies,key=lambda s:abs(s[0]-xm)+abs(s[1]-zm))[:6]
                warm=[];r=None
                for _,_,template in near:
                    r=adapt(template,fb,float(k));warm.extend(r['duals']);out=finish(r)
                    if out:return out
                # Refine the allocation only once the parameter rectangle is small.
                if depth>=23:
                    r=relax(fb,float(k),n=n,maxiter=50,warm=warm,stop=lambda r:energy_float(r,fb)[0]<cap-1e-7);lps+=1
                    energies.append((xm,zm,r));out=finish(adapt(r,fb,float(k)))
                    if out:return out
                if phase==3:break
                candidates=[]
                nearc=sorted(couplings,key=lambda s:abs(s[0]-xm)+abs(s[1]-zm))[:8]
                for _,_,template in nearc:
                    ar=adapt(template,fb,float(k));ar['lam']=template['lam']
                    val,lam=coupling_float(ar,fb,cap);candidates.append((val,lam,ar))
                if depth>=23 and r is not None:
                    c=couple(r,eu,1+3*fb[0]-2*fb[3])
                    if c and 0<c['kappa_dual']<.1:
                        cr=dict(n=n,duals=c['rows'],lam=c['lam']);couplings.append((xm,zm,cr))
                        ar=adapt(cr,fb,float(k));ar['lam']=cr['lam'];val,lam=coupling_float(ar,fb,cap);candidates.append((val,lam,ar))
                advanced=False
                for val,lam,ar in sorted(candidates,key=lambda item:item[0],reverse=True)[:3]:
                    if val<float(k)+2e-6:break
                    w=pack_boost(ar,lam)
                    kb=boost_bound(w,box,k,fcap)
                    nxt=F((kb.numerator*10**10)//kb.denominator-1,10**10)
                    if nxt<=k+F(1,10**6):continue
                    w['next_kappa']=str(nxt);boosts.append(w);k=nxt;boostcount+=1;advanced=True;break
                if not advanced:break
        if depth>=31:raise RuntimeError(('unclosed',box))
        axis=0 if xh-xl>=zh-zl else 1;mid=(box[2*axis]+box[2*axis+1])/2
        left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid;counts['split']+=1
        return dict(axis=axis,left=visit(left,depth+1),right=visit(right,depth+1))
    tree=visit([F(0),F(1,2),F(0),F(1)])
    data=dict(schema=2,lower=lower,kappa_constant='49/50',counts=counts,tree=tree)
    path=ROOT/('coupled_'+lower.replace('.','p')+'_certificate.json')
    path.write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('DONE',path.name,counts,'LPs',lps,'seconds',time.time()-start,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lower',default='1.95845');ap.add_argument('--cells',type=int,default=32);a=ap.parse_args();main(a.lower,a.cells)
