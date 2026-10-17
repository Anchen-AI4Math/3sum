"""Float-assisted tree discovery for a rigorous all-profile lower bound."""
import json,math
from fractions import Fraction as F
from explore_profiles import H,invH
from pathlib import Path
ROOT=Path(__file__).resolve().parent
EMIN=1.5*H(1/3)
def ff(t):return 0. if t>=1 else (1-t)*math.log2(1-t)
def upper_t(y):
    return F(math.ceil(invH(y)*10**10)+1,10**10) if y<1 else F(1,2)

def bound(box):
    xl,xh,hl,hh=map(float,box)
    th=upper_t(hh);theta=float(th)
    v=max(0,1-xh-2*hh)
    E=max(EMIN,(v-ff(theta))/(2*theta))
    amin=hl+2*xl
    a=min(F(3,8),box[2]+2*box[0])
    t=None
    if a>th:
        af=float(a);r=1-af
        t=upper_t(min(1,(1-hl-2*xl)/r))
        pre=max(af*EMIN,af*(v-af*ff(theta/af))/(2*theta))
        suf=max(r*EMIN,(v+af-r*ff(float(t)))/(2*float(t)))
        E=max(E,pre+suf)
    else:a=F(0)
    delta=min(xh/(E+.5-hh),2*xh/(2*E+xh))
    return delta,{'theta':str(th),'a':str(a),'t':str(t) if t else None}

def main():
    target=F('1.9533');cap=float(2-target)
    counts={'leaves':0,'empty':0,'split':0}
    def visit(box,depth=0):
        xl,xh,hl,hh=box
        if xl+hl>=F(1,2):counts['empty']+=1;return {'empty':True}
        delta,w=bound(box)
        if delta<cap-2e-9:
            counts['leaves']+=1;return w
        if depth>40:raise ValueError(('too deep',box,delta))
        axis=0 if xh-xl>=hh-hl else 1
        mid=(box[2*axis]+box[2*axis+1])/2
        left=list(box);right=list(box);left[2*axis+1]=mid;right[2*axis]=mid
        counts['split']+=1
        return {'axis':axis,'left':visit(left,depth+1),'right':visit(right,depth+1)}
    tree=visit([F(0),F(1,2),F(0),F(1,2)])
    data={'schema':1,'lower':str(target),'counts':counts,'tree':tree}
    (ROOT/'all_profile_barrier.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
    print('EXPLORATORY TREE',counts,flush=True)
if __name__=='__main__':main()
