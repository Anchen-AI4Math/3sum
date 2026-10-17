"""Bilinearly interpolated test allocations; exact corner verification.

Entropy concavity, convexity of f, and concavity of local infima lift the
four checks to the entire rectangle. See PARAMETRIC_PROOF.txt.
"""
from fractions import Fraction as F
from kappa_bound import CONSTANT
from fast_rational import entropy_lower,f_upper
from coupled_exact import min_term,base_kappa
from verify_affine import require

def vertices(box):return [(x,z) for x in box[:2] for z in box[2:]]

def summarize(node,box,k):
    n=node['n'];require(type(n) is int and 1<=n<=1000,'bad partition')
    vs=vertices(box);B=[F(0)]*4;Y=F(0)
    C=[[F(0)]*n for _ in range(4)];D=[[F(0)]*n for _ in range(4)]
    for row in node['rows']:
        j=row['j'];y=F(row['y']);ts=[list(map(F,t)) for t in row['t']]
        require(type(j) is int and 0<=j<n and len(ts)==4 and all(len(t)==n for t in ts),'bad parametric row shape')
        require(y>=0 and all(0<=t<=1 for arr in ts for t in arr),'bad row bounds')
        require(all(all(t==0 for t in arr[:j]) for arr in ts),'test uses deleted prefix')
        a=F(j,n);r=1-a;qs=[sum(arr)/n for arr in ts]
        require(all(q>0 for q in qs),'empty allocation')
        if j:
            require(a<=box[2]+k,'unavailable depth')
            thresholds=[(1-z-k)/r for x,z in vs]
        else:thresholds=[z-2*x for x,z in vs]
        require(all(q>=r/2 for q in qs) or all(entropy_lower(q/r)>=h for q,h in zip(qs,thresholds)),
                'parametric entropy interpolation not justified')
        Y+=y
        for v,arr in enumerate(ts):
            B[v]+=y*(a-sum(f_upper(t) for t in arr)/n)
            for i,t in enumerate(arr):
                C[v][i]+=2*y*t;D[v][i]+=y*(1-t)*min(2*t,F(1))
    return B,Y,C,D

def boost_bound(node,box,k,cap):
    B,Y,C,D=summarize(node,box,k);lam=F(node['lambda']);require(lam>=0,'negative lambda')
    vals=[]
    for v,(x,z) in enumerate(vertices(box)):
        require(all(c<=lam for c in C[v]),'coupling capacity exceeded')
        M=sum(min_term(lam-c,CONSTANT*(1+d)) for c,d in zip(C[v],D[v]))/len(C[v])
        vals.append(B[v]+Y*(1+3*x-2*z)-lam*(x/cap-F(1,2)+z-2*x)+M)
    return min(vals)

def energy_bound(node,box,k):
    B,Y,C,D=summarize(node,box,k);ds=[[],[]]
    for v,(x,z) in enumerate(vertices(box)):
        require(all(c<=1 for c in C[v]),'energy capacity exceeded')
        M=sum(min_term(1-c,CONSTANT*d) for c,d in zip(C[v],D[v]))/len(C[v])
        E=B[v]+Y*(1+3*x-2*z)+M
        den1=E+F(1,2)+2*x-z;den2=2*E+x
        require(den1>0 and den2>0,'nonpositive denominator')
        ds[0].append(x/den1);ds[1].append(2*x/den2)
    return min(max(ds[0]),max(ds[1]))

def leaf(node,box,cap):
    k=F(node['kappa']);base_kappa(k,box,cap)
    for boost in node.get('boosts',[]):
        nxt=F(boost['next_kappa']);require(nxt>k,'nonincreasing boost')
        require(boost_bound(boost,box,k,cap)>=nxt,'unproved parametric boost');k=nxt
    return energy_bound(node,box,k)
