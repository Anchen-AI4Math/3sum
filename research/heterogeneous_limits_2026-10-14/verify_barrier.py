"""Rational all-profile model barrier. Universal proof: LIMIT_PROOF.txt."""
from pathlib import Path
from fractions import Fraction as F
import json,sys,copy,time
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parent.parent/'3sum_certificate_1p960614_v3/3sum_certificate_v3'))
from verify_certificate import entropy,floor_dec
from exact_interval import log_iv,as_iv
from functools import lru_cache

def require(b,msg):
    if not b:raise ValueError(msg)
@lru_cache(None)
def f(t):
    require(0<=t<=1,'f domain')
    return as_iv(0) if t==1 else (1-t)*log_iv(1-t)/log_iv(2)
@lru_cache(None)
def hlo(t):return F(1) if t==F(1,2) else entropy(t).lo

def verify(data,verbose=True):
    require(data['schema']==1,'bad schema')
    lower=F(data['lower']);require(F('1.9533')<=lower<2,'bad lower target')
    cap=2-lower
    Emin=floor_dec((F(3,2)*entropy(F(1,3))).lo,21)
    counts={'leaves':0,'empty':0,'split':0};worst=F(0)
    def visit(node,box):
        nonlocal worst
        xl,xh,hl,hh=box
        if 'empty' in node:
            require(node['empty'] is True and xl+hl>=F(1,2),'false empty box')
            counts['empty']+=1;return
        if 'axis' in node:
            axis=node['axis'];require(type(axis) is int and axis in (0,1),'bad axis')
            mid=(box[2*axis]+box[2*axis+1])/2
            left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid
            counts['split']+=1
            visit(node['left'],left);visit(node['right'],right);return
        th=F(node['theta']);a=F(node['a'])
        require(0<th<F(1,2) and hlo(th)>=hh,'invalid inverse entropy witness')
        v=max(F(0),1-xh-2*hh)
        E=max(Emin,floor_dec(((v-f(th))/(2*th)).lo,21))
        if a:
            require(th<a<=hl+2*xl and a<1,'unavailable reporting depth')
            t=F(node['t']);r=1-a
            require(0<t<=F(1,2),'bad suffix entropy witness')
            require(hlo(t)>=(1-hl-2*xl)/r,'insufficient query allowance')
            pre=max(a*Emin,floor_dec((a*(v-a*f(th/a))/(2*th)).lo,21))
            suf=max(r*Emin,floor_dec(((v+a-r*f(t))/(2*t)).lo,21))
            E=max(E,pre+suf)
        den=E+F(1,2)-hh;require(den>0,'nonpositive denominator')
        delta=min(xh/den,2*xh/(2*E+xh))
        require(delta<cap,'box fails lower bound')
        worst=max(worst,delta);counts['leaves']+=1
    visit(data['tree'],[F(0),F(1,2),F(0),F(1,2)])
    require(counts==data['counts'],'count mismatch')
    out={'scope':'all finite homogeneous or heterogeneous profiles, arbitrary order, c>=3, beta<0; same ledger',
         'lower':str(lower),'counts':counts,'worst_saving_upper':as_iv(worst).display(24)}
    if verbose:print(json.dumps(out,indent=2));print('PASS complete continuous parameter cover, exact rationals only.')
    return out

if __name__=='__main__':
    data=json.loads((ROOT/'all_profile_barrier.json').read_text())
    result=verify(data)
    for name,change in [('false bound',lambda z:z.update(lower='1.97')),
                        ('missing cover',lambda z:z.update(tree={'empty':True}))]:
        z=copy.deepcopy(data);change(z)
        try:verify(z,False)
        except ValueError:print('PASS rejection:',name)
        else:raise ValueError('accepted false certificate '+name)
    (ROOT/'barrier_verification.json').write_text(json.dumps(result,indent=2)+'\n')
