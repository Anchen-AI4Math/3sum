"""Exact proof checker for position-coupled all-profile lower certificates."""
from pathlib import Path
from fractions import Fraction as F
import json,copy,time,argparse,gzip
from kappa_bound import prove,CONSTANT
from fast_rational import entropy_lower,f_upper,as_iv
from verify_affine import require,delta_bound
from coupled_exact import EMIN,leaf
ROOT=Path(__file__).resolve().parent

def verify(data,verbose=True):
    require(data['schema'] in (2,3),'bad schema')
    if data['schema']==3:
        from parametric_exact import leaf as check_leaf
    else:check_leaf=leaf
    require(F(data['kappa_constant'])==CONSTANT,'unproved constant')
    lower=F(data['lower']);require(1<lower<2,'bad target');cap=2-lower
    counts=dict(empty=0,base=0,initial=0,dual=0,split=0)
    rows=boosts=corrected=F(0);worst=F(0)
    def visit(node,box):
        nonlocal rows,boosts,corrected,worst
        xl,xh,zl,zh=box
        if 'axis' in node:
            axis=node['axis'];require(type(axis) is int and axis in (0,1),'bad split')
            mid=(box[2*axis]+box[2*axis+1])/2
            left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid
            counts['split']+=1;visit(node['left'],left);visit(node['right'],right);return
        kind=node['kind'];require(kind in ('empty','base','initial','dual'),'bad leaf kind');counts[kind]+=1
        if kind=='empty':
            require(zh<=2*xl or zl>=xh+F(1,2),'false empty region');return
        if kind=='base':d=delta_bound(EMIN,F(0),box)
        elif kind=='initial':
            th=F(node['theta']);require(0<th<=F(1,2),'bad theta')
            require(entropy_lower(th)>=min(F(1,2),zh-2*xl),'insufficient initial mass')
            d=delta_bound(-f_upper(th)/(2*th),1/(2*th),box)
        else:
            d=check_leaf(node,box,cap)
            rows+=len(node['rows'])+sum(len(s['rows']) for s in node.get('boosts',[]))
            boosts+=len(node.get('boosts',[]));corrected+=(data['schema']==3 or node.get('gamma_correction',False))
        require(d<cap,'leaf fails target');worst=max(worst,d)
        if verbose and kind=='dual' and counts['dual']%500==0:print('checked',counts['dual'],'dual regions,',int(boosts),'coupling boosts',flush=True)
    visit(data['tree'],[F(0),F(1,2),F(0),F(1)])
    require(counts==data['counts'],'coverage counts mismatch')
    return dict(schema=data['schema'],lower=str(lower),scope='all finite real c>=3 profiles, arbitrary order and stage count; twelve-cost certification model, beta<0',
                counts=counts,dual_rows_checked=int(rows),allocation_vertices_checked=int(rows)*(4 if data['schema']==3 else 1),coupling_boosts=int(boosts),finite_c_corrected_regions=int(corrected),
                worst_conditional_delta_upper=as_iv(worst).display(24),status='PASS: exact complete continuous parameter cover')

def first(node,predicate,change):
    if predicate(node):change(node);return True
    if 'axis' in node:return first(node['left'],predicate,change) or first(node['right'],predicate,change)
    return False

def main(path):
    start=time.time();local=prove()
    if path.exists():data=json.loads(path.read_text())
    else:
        with gzip.open(path.with_suffix(path.suffix+'.gz'),'rt') as source:data=json.load(source)
    result=verify(data)
    isdual=lambda n:n.get('kind')=='dual'
    hasboost=lambda n:bool(n.get('boosts'))
    tests=[('false lower bound',lambda d:d.update(lower='1.99')),
           ('false empty region',lambda d:d.update(tree=dict(kind='empty'))),
           ('inflated local constant',lambda d:d.update(kappa_constant='99/100')),
           ('overweight energy dual',lambda d:first(d['tree'],isdual,lambda n:[s.update(y=str(100*F(s['y']))) for s in n['rows']])),
           ('inflated base kappa',lambda d:first(d['tree'],isdual,lambda n:n.update(kappa=str(2*F(n['kappa']))))),
           ('inflated coupled kappa',lambda d:first(d['tree'],hasboost,lambda n:n['boosts'][0].update(next_kappa='1'))),
           ('missing coupling energy multiplier',lambda d:first(d['tree'],hasboost,lambda n:n['boosts'][0].update({'lambda':'0'})))]
    rejected=[]
    for name,change in tests:
        bad=copy.deepcopy(data);change(bad)
        try:verify(bad,False)
        except ValueError:rejected.append(name)
        else:raise ValueError('accepted forgery: '+name)
    result.update(local_inequality=local,rejected_forgeries=rejected,elapsed_seconds=time.time()-start)
    out=path.with_name(path.name.replace('_certificate','_verification'))
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('certificate',nargs='?',default='coupled_1p9584_certificate.json');a=ap.parse_args();main(ROOT/a.certificate)
