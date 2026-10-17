"""Discover compact complete covers using bilinear test allocations."""
from fractions import Fraction as F
import math,json,time,argparse
import numpy as np
from affine_search import ROOT,relax,adapt,EMIN,f,invH,delta_bound
from coupling_explore import couple,minimum_term
from parametric_exact import vertices,boost_bound,energy_bound

def adapt4(template,box,k):
    n=template['n'];rows=[]
    for row in template['duals']:
        j=row['j'];a=j/n;r=1-a
        if j and a>box[2]+k:continue
        half=j and 1-box[2]-k>=r
        arr=[]
        for x,z in vertices(box):
            q=(r/2 if half else r*invH((1-z-k)/r)) if j else invH(z-2*x)
            q+=2e-10;t=np.array(row['t']);old=t.sum()/n
            if old<q:t[j:]+=(q-old)/(r-old)*(1-t[j:])
            elif old>q:t[j:]*=q/old
            arr.append(t.tolist())
        rows.append(dict(j=j,y=row['y'],t=arr))
    return dict(n=n,duals=rows,lam=template.get('lam',0))

def raw(r):
    n=r['n'];B=np.zeros(4);C=np.zeros((4,n));D=C.copy();Y=0.
    for row in r['duals']:
        y=row['y'];t=np.array(row['t']);C+=2*y*t;D+=y*(1-t)*np.minimum(2*t,1)
        B+=y*(row['j']/n-f(t).sum(axis=1)/n);Y+=y
    return B,Y,C,D

def dfloat(E,box):
    d1=[];d2=[]
    for e,(x,z) in zip(E,vertices(box)):
        if e+.5+2*x-z<=0 or 2*e+x<=0:return 1.
        d1.append(x/(e+.5+2*x-z));d2.append(2*x/(2*e+x))
    return min(max(d1),max(d2))

def efloat(r,box):
    B,Y,C,D=raw(r);norm=C.max() or 1.;B/=norm;Y/=norm;C/=norm;D/=norm
    v=np.array([1+3*x-2*z for x,z in vertices(box)]);best=(1.,1.)
    for s in [1.,.9995,.999,.998,.997,.995,.99,.98,.95]:
        M=np.array([minimum_term(np.maximum(0,1-s*c),.98*s*d).mean() for c,d in zip(C,D)])
        val=dfloat(s*B+s*Y*v+M,box)
        if val<best[0]:best=val,s
    return best

def kfloat(r,box,cap):
    B,Y,C,D=raw(r);lam=max(r['lam'],C.max()+1e-11)
    M=np.array([minimum_term(lam-c,.98*(1+d)).mean() for c,d in zip(C,D)])
    vals=[b+Y*(1+3*x-2*z)-lam*(x/cap-.5+z-2*x)+m for b,m,(x,z) in zip(B,M,vertices(box))]
    return min(vals),lam

def pack4(r,scale=None,lam=None):
    n=r['n'];rows=[]
    for row in r['duals']:
        y=F(math.floor(row['y']*10**12),10**12)
        if y==0:continue
        ts=[[F(min(10**6,math.ceil(max(0,t)*10**6)),10**6) for t in arr] for arr in row['t']]
        rows.append(dict(j=row['j'],y=y,t=ts))
    norm=max(sum(2*s['y']*s['t'][v][i] for s in rows) for v in range(4) for i in range(n)) or F(1)
    if scale is not None:
        for s in rows:s['y']*=F(str(scale))/norm
    out=dict(n=n,rows=[dict(j=s['j'],y=str(s['y']),t=[list(map(str,arr)) for arr in s['t']]) for s in rows])
    if lam is not None:out['lambda']=str(max(F(math.ceil(lam*10**12),10**12),norm+F(1,10**12)))
    return out

def main(lower='1.95845',n=32):
    cap=2-float(lower);fcap=2-F(lower);start=time.time();lps=0
    saved=ROOT/f'parametric_templates_{n}.json'
    if saved.exists():
        data=json.loads(saved.read_text());energies=data['energies'];couplings=data['couplings']
    else:
        energies=[];couplings=[]
        for x,z in [(.17,.65),(.18,.65),(.1825,.66),(.19,.66),(.19,.67),(.20,.67),(.21,.68)]:
            eu=x/cap-.5+z-2*x;k=.98*2**(-2*eu)
            for _ in range(3):
                r=relax([x,x,z,z],k,n=n,maxiter=150);energies.append((x,z,r));lps+=1
                if efloat(adapt4(r,[x,x,z,z],k),[x,x,z,z])[0]<cap-1e-6:break
                c=couple(r,eu,1+3*x-2*z)
                if not c or c['kappa_dual']<=k+1e-6 or c['kappa_dual']>.1:break
                cr=dict(n=n,duals=c['rows'],lam=c['lam']);couplings.append((x,z,cr));k=c['kappa_dual']-1e-8
        saved.write_text(json.dumps(dict(energies=energies,couplings=couplings),separators=(',',':'))+'\n')
    print('templates',len(energies),len(couplings),'seconds',round(time.time()-start,1),flush=True)
    counts=dict(empty=0,base=0,initial=0,dual=0,split=0);seen=0
    journal=ROOT/('parametric_'+lower.replace('.','p')+'_leaves.jsonl');cache={}
    if journal.exists():
        for line in journal.read_text().splitlines():
            e=json.loads(line);cache[tuple(e['box'])]=e['node']
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
        nonlocal seen,lps
        seen+=1;xl,xh,zl,zh=box;fb=list(map(float,box));xm=float((xl+xh)/2);zm=float((zl+zh)/2);point=[xm,xm,zm,zm]
        if seen%100==0:print('cover',seen,counts,'LPs',lps,'seconds',round(time.time()-start,1),'depth',depth,'box',fb,flush=True)
        if zh<=2*xl or zl>=xh+F(1,2):counts['empty']+=1;return dict(kind='empty')
        if delta_bound(EMIN,0,fb)<cap-1e-9:counts['base']+=1;return dict(kind='base')
        hh=min(.5,float(zh-2*xl));th=min(F(1,2),F(math.ceil(invH(hh)*10**10)+1,10**10));t=float(th)
        if t>0 and delta_bound(-float(f(t))/(2*t),1/(2*t),fb)<cap-1e-9:
            counts['initial']+=1;return dict(kind='initial',theta=str(th))
        eu=min(float(xh)/cap-.5+float(zh-2*xh),float(xh)/cap-float(xh)/2)
        basek=F(math.floor(.98*2**(-2*eu)*10**11),10**11);k=basek;boosts=[]
        def finish(r):
            d,s=efloat(r,fb)
            if d>=cap-5e-8:return None
            w=pack4(r,scale=s)
            try:bound=energy_bound(w,box,k)
            except ValueError:return None
            if bound>=fcap-F(1,10**9):return None
            counts['dual']+=1;return dict(kind='dual',kappa=str(basek),boosts=boosts.copy(),**w)
        if max(xh-xl,zh-zl)<=F(1,16):
            for phase in range(5):
                near=sorted(energies,key=lambda s:abs(s[0]-xm)+abs(s[1]-zm))[:7]
                warm=[];r=None
                for _,_,template in near:
                    ar=adapt4(template,fb,float(k));out=finish(ar)
                    if out:return out
                    warm.extend(adapt(template,point,float(k))['duals'])
                if depth>=19:
                    r=relax(point,float(k),n=n,maxiter=65,warm=warm,
                            stop=lambda rr:efloat(adapt4(rr,fb,float(k)),fb)[0]<cap-1e-7);lps+=1
                    energies.append((xm,zm,r));out=finish(adapt4(r,fb,float(k)))
                    if out:return out
                if phase==4:break
                candidates=[]
                for _,_,template in sorted(couplings,key=lambda s:abs(s[0]-xm)+abs(s[1]-zm))[:10]:
                    ar=adapt4(template,fb,float(k));val,lam=kfloat(ar,fb,cap);candidates.append((val,lam,ar))
                if r is not None:
                    c=couple(r,xm/cap-.5+zm-2*xm,1+3*xm-2*zm)
                    if c and 0<c['kappa_dual']<.1:
                        cr=dict(n=n,duals=c['rows'],lam=c['lam']);couplings.append((xm,zm,cr))
                        ar=adapt4(cr,fb,float(k));val,lam=kfloat(ar,fb,cap);candidates.append((val,lam,ar))
                advanced=False
                for val,lam,ar in sorted(candidates,key=lambda t:t[0],reverse=True)[:3]:
                    if val<float(k)+2e-6:break
                    w=pack4(ar,lam=lam)
                    try:kb=boost_bound(w,box,k,fcap)
                    except ValueError:continue
                    nxt=F((kb.numerator*10**10)//kb.denominator-1,10**10)
                    if nxt<=k+F(1,10**6):continue
                    w['next_kappa']=str(nxt);boosts.append(w);k=nxt;advanced=True;break
                if not advanced:break
        if depth>=30:raise RuntimeError(('unclosed',box))
        axis=0 if xh-xl>=zh-zl else 1;mid=(box[2*axis]+box[2*axis+1])/2
        left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid;counts['split']+=1
        return dict(axis=axis,left=visit(left,depth+1),right=visit(right,depth+1))
    tree=visit([F(0),F(1,2),F(0),F(1)])
    path=ROOT/('parametric_'+lower.replace('.','p')+'_certificate.json')
    path.write_text(json.dumps(dict(schema=3,lower=lower,kappa_constant='49/50',counts=counts,tree=tree),separators=(',',':'))+'\n')
    saved.write_text(json.dumps(dict(energies=energies,couplings=couplings),separators=(',',':'))+'\n')
    print('DONE',path.name,counts,'LPs',lps,'seconds',time.time()-start,flush=True)

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--lower',default='1.95845');ap.add_argument('--cells',type=int,default=32);a=ap.parse_args();main(a.lower,a.cells)
