"""Exact complete-cover proof for ALL finite profiles, not a sampled grid.

Only Python standard library and inherited rational interval arithmetic.
The cell partition discretizes test functions, never the unknown profile.
"""
from pathlib import Path
from fractions import Fraction as F
import json,copy,time,gzip
from fast_rational import entropy_lower,f_upper,as_iv,log2,LN2
ROOT=Path(__file__).resolve().parent

def load_certificate(path):
    """Read an optional local JSON, or its lossless Git-stored gzip copy."""
    if path.exists():
        return json.loads(path.read_text(encoding='utf-8'))
    with gzip.open(path.with_suffix(path.suffix+'.gz'),'rt',encoding='utf-8') as source:
        return json.load(source)

def require(ok,msg):
    if not ok:raise ValueError(msg)

def verify(data,verbose=True):
    require(data['schema'] in (1,2),'bad schema')
    require(LN2.hi<F(45,64),'kappa constant proof failed')
    lower=F(data['lower']);require(1<lower<2,'bad target')
    cap=2-lower;Emin=F(3,2)*entropy_lower(F(1,3))
    counts={'empty':0,'analytic':0,'dual':0,'split':0};worst=F(0);rowcount=0
    def visit(node,box):
        nonlocal worst,rowcount
        xl,xh,hl,hh=box
        if 'axis' in node:
            axis=node['axis'];require(type(axis) is int and axis in (0,1),'bad axis')
            mid=(box[2*axis]+box[2*axis+1])/2
            l=list(box);r=list(box);l[2*axis+1]=mid;r[2*axis]=mid
            counts['split']+=1;visit(node['left'],l);visit(node['right'],r);return
        kind=node['kind'];require(kind in ('empty','analytic','dual'),'bad leaf kind')
        counts[kind]+=1
        if kind=='empty':require(xl+hl>=F(1,2),'false empty region');return
        v=max(F(0),1-xh-2*hh)
        if kind=='analytic':
            th=F(node['theta']);a=F(node['a'])
            require(0<th<F(1,2) and entropy_lower(th)>=hh,'bad initial entropy witness')
            E=max(Emin,(v-f_upper(th))/(2*th))
            if a:
                require(th<a<=hl+2*xl and a<1,'unavailable report depth')
                t=F(node['t']);r=1-a
                require(0<t<=F(1,2) and entropy_lower(t)>=(1-hl-2*xl)/r,'bad suffix witness')
                pre=max(a*Emin,a*(v-a*f_upper(th/a))/(2*th))
                suf=max(r*Emin,(v+a-r*f_upper(t))/(2*t))
                E=max(E,pre+suf)
        else:
            n=node['n'];require(type(n) is int and 1<=n<=1000,'bad test partition')
            k=F(node.get('kappa','0'));require(k>=0,'negative kappa witness')
            if k:
                require(data['schema']==2,'unexpected conditional kappa')
                Eup=xh/cap-F(1,2)+hh
                require(log2(F(4,5)/k).lo>=2*Eup,'unproved kappa lower bound')
            capacities=[F(0)]*n;E=Emin
            for row in node['rows']:
                j=row['j'];y=F(row['y']);ts=[F(t) for t in row['t']]
                require(type(j) is int and 0<=j<n and len(ts)==n,'bad row shape')
                require(y>=0 and all(0<=t<=1 for t in ts),'bad row bounds')
                require(all(t==0 for t in ts[:j]),'test uses deleted prefix')
                a=F(j,n);r=1-a;q=sum(ts)/n
                require(q>0,'empty allocation')
                if j==0:
                    require(q>=F(1,2) or entropy_lower(q)>=hh,'insufficient initial test mass')
                else:
                    require(a<=hl+2*xl+k,'report depth not guaranteed')
                    require(q>=r/2 or entropy_lower(q/r)>=(1-hl-2*xl-k)/r,'insufficient report test mass')
                for i,t in enumerate(ts):capacities[i]+=2*y*t
                rhs=v+a-sum(f_upper(t) for t in ts)/n
                E+=y*(rhs-2*Emin*q)
                rowcount+=1
            require(all(c<=1 for c in capacities),'dual exceeds pointwise energy budget')
            require(E>=Emin,'unhelpful dual')
        den=E+F(1,2)-hh;require(den>0,'bad denominator')
        d=min(xh/den,2*xh/(2*E+xh))
        require(d<cap,'leaf fails claimed lower bound')
        worst=max(worst,d)
        if verbose and kind=='dual' and counts['dual']%2000==0:
            print('EXACT CHECKED dual regions:',counts['dual'],'rows:',rowcount,flush=True)
    visit(data['tree'],[F(0),F(1,2),F(0),F(1,2)])
    require(counts==data['counts'],'coverage counts mismatch')
    result={'scope':'all finite expansion profiles c>=3, arbitrary order and number of pieces; beta<0, same cost/box model',
            'lower':str(lower),'counts':counts,'dual_rows_checked':rowcount,
            'worst_delta_upper':as_iv(worst).display(24),'verification':'exact rational interval arithmetic; no floating optimizer'}
    if verbose:print(json.dumps(result,indent=2));print('PASS complete continuous parameter cover.')
    return result

def corrupt_dual(node):
    if node.get('kind')=='dual':
        for row in node['rows']:row['y']=str(100*F(row['y']))
        return True
    if 'axis' in node:return corrupt_dual(node['left']) or corrupt_dual(node['right'])
    return False

def corrupt_kappa(node):
    if node.get('kind')=='dual' and F(node.get('kappa','0'))>0:
        node['kappa']=str(2*F(node['kappa']));return True
    if 'axis' in node:return corrupt_kappa(node['left']) or corrupt_kappa(node['right'])
    return False

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--kappa',action='store_true');ap.add_argument('--fast',action='store_true');ap.add_argument('--sprint',action='store_true');ap.add_argument('--prefix');args=ap.parse_args()
    prefix=args.prefix or ('kappa_multidepth_sprint' if args.sprint else 'kappa_multidepth_fast' if args.fast else 'kappa_multidepth' if args.kappa else 'multidepth')
    start=time.time();data=load_certificate(ROOT/(prefix+'_certificate.json'))
    result=verify(data)
    trials=[('false bound',lambda d:d.update(lower='1.99')),
                        ('missing cover',lambda d:d.update(tree={'kind':'empty'})),
                        ('overweight dual',lambda d:corrupt_dual(d['tree']))]
    if data['schema']==2:trials.append(('inflated kappa',lambda d:corrupt_kappa(d['tree'])))
    for name,change in trials:
        forged=copy.deepcopy(data);change(forged)
        try:verify(forged,False)
        except ValueError:print('PASS rejection:',name,flush=True)
        else:raise ValueError('accepted forged certificate '+name)
    result['elapsed_seconds']=time.time()-start
    (ROOT/(prefix+'_verification.json')).write_text(json.dumps(result,indent=2)+'\n')
