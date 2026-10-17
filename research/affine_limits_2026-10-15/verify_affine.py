"""Independent exact proof: complete binary cover, affine correlations retained.

No NumPy/SciPy or discovery code is imported. All decisions use Fraction
and integer-rounded logarithm enclosures. See PROOF.txt for the derivation.
"""
from pathlib import Path
from fractions import Fraction as F
import json,time,copy,argparse
from kappa_bound import prove,CONSTANT
from fast_rational import entropy_lower,f_upper,log2,as_iv
ROOT=Path(__file__).resolve().parent

def require(ok,msg):
    if not ok:raise ValueError(msg)

def delta_bound(A,Y,box):
    bounds=[[],[]]
    for x in box[:2]:
        for z in box[2:]:
            E=A+Y*(1+3*x-2*z)
            d1=E+F(1,2)+2*x-z;d2=2*E+x
            require(d1>0 and d2>0,'nonpositive affine denominator')
            bounds[0].append(x/d1);bounds[1].append(2*x/d2)
    # Each positive linear-fractional function reaches its max at a vertex.
    # Max(min(f,g)) is NOT in general bounded by max_vertex min(f,g).
    return min(max(bounds[0]),max(bounds[1]))

def verify(data,verbose=True):
    require(data['schema']==1,'bad schema')
    require(F(data['kappa_constant'])==CONSTANT,'unproved local constant')
    lower=F(data['lower']);require(1<lower<2,'bad target');cap=2-lower
    Emin=F(3,2)*entropy_lower(F(1,3))
    counts=dict(empty=0,base=0,initial=0,dual=0,split=0);rows_checked=0;worst=F(0)
    def visit(node,box):
        nonlocal rows_checked,worst
        xl,xh,zl,zh=box
        if 'axis' in node:
            axis=node['axis'];require(type(axis) is int and axis in (0,1),'bad split axis')
            mid=(box[2*axis]+box[2*axis+1])/2
            left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid
            counts['split']+=1;visit(node['left'],left);visit(node['right'],right);return
        kind=node['kind'];require(kind in ('empty','base','initial','dual'),'bad leaf kind');counts[kind]+=1
        if kind=='empty':
            require(zh<=2*xl or zl>=xh+F(1,2),'false empty region');return
        hh=min(F(1,2),zh-2*xl)
        if kind=='base':A=Emin;Y=F(0)
        elif kind=='initial':
            th=F(node['theta']);require(0<th<=F(1,2),'bad theta')
            require(entropy_lower(th)>=hh,'insufficient initial mass')
            A=-f_upper(th)/(2*th);Y=1/(2*th)
        else:
            k=F(node['kappa']);require(k>0,'bad kappa')
            Eup=min(xh/cap-F(1,2)+zh-2*xh,xh/cap-xh/2)
            require(log2(CONSTANT/k).lo>=2*Eup,'unproved conditional kappa')
            n=node['n'];require(type(n) is int and 1<=n<=1000,'bad partition')
            capacities=[F(0)]*n;A=Emin;Y=F(0)
            for row in node['rows']:
                j=row['j'];y=F(row['y']);ts=list(map(F,row['t']))
                require(type(j) is int and 0<=j<n and len(ts)==n,'bad row shape')
                require(y>=0 and all(0<=t<=1 for t in ts),'bad row bounds')
                require(all(t==0 for t in ts[:j]),'test uses deleted prefix')
                a=F(j,n);r=1-a;q=sum(ts)/n
                require(q>0,'empty allocation')
                if j==0:
                    require(q>=F(1,2) or entropy_lower(q)>=hh,'insufficient initial mass')
                else:
                    require(a<=zl+k,'unavailable report depth')
                    require(q>=r/2 or entropy_lower(q/r)>=(1-zl-k)/r,'insufficient report mass')
                for i,t in enumerate(ts):capacities[i]+=2*y*t
                A+=y*(a-sum(f_upper(t) for t in ts)/n-2*Emin*q);Y+=y
                rows_checked+=1
            require(all(c<=1 for c in capacities),'dual exceeds energy budget')
        d=delta_bound(A,Y,box)
        require(d<cap,'leaf fails target bound')
        worst=max(worst,d)
        if verbose and kind=='dual' and counts['dual']%1000==0:print('checked',counts['dual'],'dual regions',flush=True)
    visit(data['tree'],[F(0),F(1,2),F(0),F(1)])
    require(counts==data['counts'],'coverage counts mismatch')
    return dict(lower=str(lower),scope='all finite real expansion profiles c>=3, arbitrary order; original twelve-cost model, beta<0',
                counts=counts,dual_rows_checked=rows_checked,worst_conditional_delta_upper=as_iv(worst).display(24),
                status='PASS: exact rational complete continuous cover')

def change_first(node,fn):
    if node.get('kind')=='dual':fn(node);return True
    if 'axis' in node:return change_first(node['left'],fn) or change_first(node['right'],fn)
    return False

def main(path):
    start=time.time();local=prove();data=json.loads(path.read_text());result=verify(data)
    tests=[('false lower bound',lambda d:d.update(lower='1.99')),
           ('false empty region',lambda d:d.update(tree=dict(kind='empty'))),
           ('inflated local constant',lambda d:d.update(kappa_constant='99/100')),
           ('overweight dual',lambda d:change_first(d['tree'],lambda n:[s.update(y=str(100*F(s['y']))) for s in n['rows']])),
           ('inflated kappa',lambda d:change_first(d['tree'],lambda n:n.update(kappa=str(2*F(n['kappa'])))))]
    rejected=[]
    for name,change in tests:
        bad=copy.deepcopy(data);change(bad)
        try:verify(bad,False)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted forged certificate: '+name)
    result.update(local_inequality=local,rejected_forgeries=rejected,elapsed_seconds=time.time()-start)
    out=path.with_name(path.name.replace('_certificate','_verification'))
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('certificate',nargs='?',default='affine_1p95815_certificate.json');args=ap.parse_args();main(ROOT/args.certificate)
