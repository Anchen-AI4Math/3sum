"""Exact fixed-layout lower bound; no optimizer, numpy or scipy imported."""
from verify_profile import ROOT,F,entropy,gamma,as_iv,floor_dec,ceil_dec,weights,require
from functools import lru_cache
import json,copy

@lru_cache(None)
def Hlo(t):return F(1) if t==F(1,2) else entropy(t).lo

def verify(data,verbose=True):
    require(data['schema']==1,'bad schema')
    lower=F(data['lower']);cap=2-lower
    require(1<lower<2,'bad lower bound')
    cs=data['expansions'];ws=[F(w) for w in data['weights']]
    require(len(cs)==len(ws)>0 and all(type(c) is int and c>=3 for c in cs),'bad profile')
    require(all(w>0 for w in ws) and sum(ws)==1,'bad weights')
    Es=[F(c,2)*entropy(F(1,c)) for c in cs]
    ks=[2*c*entropy(F(1,2*c))-2*E-1 for c,E in zip(cs,Es)]
    El=floor_dec(sum(w*E for w,E in zip(ws,Es)).lo,21)
    kl=floor_dec(sum(w*k for w,k in zip(ws,ks)).lo,21)
    counts={};largest=F(0);smallest=None

    @lru_cache(None)
    def Gupper(a,q):
        w=weights(ws,a);require(0<=q<=1-a,'allocation domain')
        active=sorted((j for j in range(len(cs)) if w[j]>0),key=lambda j:cs[j])
        W=C=F(0)
        for i,j in enumerate(active):
            W+=w[j];C+=w[j]*cs[j];lam=(W-q)/C
            if i+1==len(active) or lam>=F(1,cs[active[i+1]]):break
        ts=[max(F(0),1-c*lam) for c in cs]
        require(all(0<=t<=1 for t in ts),'allocation bounds')
        require(sum(wi*t for wi,t in zip(w,ts))==q,'allocation mass')
        # Feasible allocation gives an UPPER bound on the minimum Gamma.
        return ceil_dec(sum(wi*gamma(c,t) for wi,c,t in zip(w,cs,ts)).hi,21)

    def visit(node,box):
        nonlocal largest,smallest
        xl,xh,hl,hh=box
        if 'axis' in node:
            axis=node['axis'];require(type(axis) is int and axis in (0,1),'bad axis')
            mid=(box[2*axis]+box[2*axis+1])/2
            l=list(box);r=list(box);l[2*axis+1]=mid;r[2*axis]=mid
            visit(node['left'],l);visit(node['right'],r);kind='split'
        else:
            kind=node['kind'];v=max(F(0),1-xh-2*hh)
            if kind=='empty':require(xl+hl>=F(1,2),'false empty region')
            elif kind=='cap':
                d=min(xh/(El+F(1,2)-hh),2*xh/(2*El+xh))
                require(d<cap,'failed cost cap');largest=max(largest,d)
            elif kind=='initial':
                th=F(node['theta']);require(0<th<F(1,2) and Hlo(th)>=hh,'bad initial witness')
                margin=v-Gupper(F(0),th);require(margin>0,'initial exclusion failed')
                smallest=margin if smallest is None else min(smallest,margin)
            elif kind in ('report','negative_query'):
                a=F(node['a']);require(0<a<1 and a<=hl+2*xl+kl,'unavailable report depth')
                Q=1-hl-2*xl-kl
                if kind=='negative_query':require(Q<0,'false negative query allowance')
                else:
                    t=F(node['t']);require(0<t<=F(1,2) and Hlo(t)>=Q/(1-a),'bad report witness')
                    margin=v+a-Gupper(a,(1-a)*t);require(margin>0,'report exclusion failed')
                    smallest=margin if smallest is None else min(smallest,margin)
            else:raise ValueError('unknown leaf')
        counts[kind]=counts.get(kind,0)+1
    visit(data['tree'],[F(0),F(1,2),F(0),F(1,2)])
    require(counts==data['counts'],'count mismatch')
    result={'scope':'fixed rational profile; all epsilon,beta<0,S,tau and admissible threshold schedules in the same ledger',
            'lower':str(lower),'counts':counts,'largest_cap_delta':as_iv(largest).display(24),
            'smallest_exclusion_margin':as_iv(smallest).display(24)}
    if verbose:print(json.dumps(result,indent=2));print('PASS complete exact fixed-profile parameter cover.')
    return result

if __name__=='__main__':
    data=json.loads((ROOT/'fixed_profile_barrier.json').read_text())
    result=verify(data)
    # Ensure it refers to exactly the upper-certificate layout, not just nearby floats.
    upper=json.loads((ROOT/'profile_certificate.json').read_text())
    require(data['expansions']==upper['expansions'] and data['weights']==upper['weights'],'upper/lower layout mismatch')
    for name,change in [('false lower bound',lambda z:z.update(lower='1.96')),
                        ('false root exclusion',lambda z:z.update(tree={'kind':'empty'}))]:
        z=copy.deepcopy(data);change(z)
        try:verify(z,False)
        except ValueError:print('PASS rejection:',name)
        else:raise ValueError('accepted forged certificate '+name)
    (ROOT/'fixed_barrier_verification.json').write_text(json.dumps(result,indent=2)+'\n')
