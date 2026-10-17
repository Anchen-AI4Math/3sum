"""Exact local dual calculations shared by discovery and the proof checker.

This file imports only standard-library rational arithmetic and the independently
proved local constant. It never calls a floating optimizer.
"""
from fractions import Fraction as F
from kappa_bound import CONSTANT
from fast_rational import entropy_lower,f_upper,log2,LN2
from verify_affine import require,delta_bound
EMIN=F(3,2)*entropy_lower(F(1,3))

def min_term(b,g):
    """Lower bound for inf_{e>=EMIN} b*e+g*4^-e."""
    require(b>=0 and g>=0,'negative local dual coefficient')
    if b==0:return F(0)
    if g==0:return b*EMIN
    # Unrestricted minimizer e*=log2(2 ln(2) g/b)/2. Taking the maximum
    # with b*EMIN is safe, even if that minimizer lies outside the domain.
    free=b*(log2(2*LN2.lo*g/b).lo+1/LN2.hi)/2
    return max(b*EMIN,free)

def rows_summary(node,box,k):
    xl,xh,zl,zh=box;hh=min(F(1,2),zh-2*xl)
    n=node['n'];require(type(n) is int and 1<=n<=1000,'bad partition')
    caps=[F(0)]*n;gs=[F(0)]*n;B=Y=F(0)
    for row in node['rows']:
        j=row['j'];y=F(row['y']);ts=list(map(F,row['t']))
        require(type(j) is int and 0<=j<n and len(ts)==n,'bad row shape')
        require(y>=0 and all(0<=t<=1 for t in ts),'bad row bounds')
        require(all(t==0 for t in ts[:j]),'test uses deleted prefix')
        a=F(j,n);r=1-a;q=sum(ts)/n;require(q>0,'empty allocation')
        if j==0:require(q>=F(1,2) or entropy_lower(q)>=hh,'insufficient initial mass')
        else:
            require(a<=zl+k,'unavailable report depth')
            require(q>=r/2 or entropy_lower(q/r)>=(1-zl-k)/r,'insufficient report mass')
        for i,t in enumerate(ts):
            caps[i]+=2*y*t;gs[i]+=F(8,5)*y*t*(1-t)
        B+=y*(a-sum(f_upper(t) for t in ts)/n);Y+=y
    return B,Y,caps,gs

def base_kappa(k,box,cap):
    xl,xh,zl,zh=box
    eup=min(xh/cap-F(1,2)+zh-2*xh,xh/cap-xh/2)
    require(k>0 and log2(CONSTANT/k).lo>=2*eup,'unproved base kappa')

def kappa_correction(node):
    """Sum y*m(t), where gamma <= 2Et+f-m(t)*k_c (see PROOF.txt)."""
    n=node['n'];ds=[F(0)]*n
    for row in node['rows']:
        y=F(row['y'])
        for i,raw in enumerate(row['t']):
            t=F(raw);ds[i]+=y*(1-t)*min(2*t,F(1))
    return ds

def boost_bound(boost,box,k,cap):
    B,Y,C,_=rows_summary(boost,box,k);lam=F(boost['lambda'])
    require(lam>=0 and all(c<=lam for c in C),'coupling dual exceeds lambda')
    stronger=boost.get('local_kappa_correction',False)
    require(type(stronger) is bool,'bad local kappa correction flag')
    ds=kappa_correction(boost) if stronger else [F(0)]*len(C)
    M=sum(min_term(lam-c,CONSTANT*(1+d)) for c,d in zip(C,ds))/len(C)
    # Encoding energy upper bound is affine in x,z. Retain that correlation.
    vals=[B+Y*(1+3*x-2*z)-lam*(x/cap-F(1,2)+z-2*x)+M
          for x in box[:2] for z in box[2:]]
    return min(vals)

def energy_bound(node,box,k):
    B,Y,C,G=rows_summary(node,box,k)
    require(all(c<=1 for c in C),'energy dual exceeds capacity')
    correction=node.get('gamma_correction',False)
    require(type(correction) is bool,'bad gamma flag')
    stronger=node.get('local_kappa_correction',False)
    require(type(stronger) is bool,'bad local kappa correction flag')
    if stronger:
        require(correction,'local correction requires gamma correction')
        G=[max(g,CONSTANT*d) for g,d in zip(G,kappa_correction(node))]
    if correction:
        require(LN2.hi<F(45,64),'unproved finite-c correction constant')
        M=sum(min_term(1-c,g) for c,g in zip(C,G))/len(C)
    else:M=EMIN*(1-sum(C)/len(C))
    return delta_bound(B+M,Y,box)

def leaf(node,box,cap):
    k=F(node['kappa']);base_kappa(k,box,cap)
    for boost in node.get('boosts',[]):
        nxt=F(boost['next_kappa']);require(nxt>k,'nonincreasing kappa boost')
        require(boost_bound(boost,box,k,cap)>=nxt,'unproved kappa boost')
        k=nxt
    return energy_bound(node,box,k)
