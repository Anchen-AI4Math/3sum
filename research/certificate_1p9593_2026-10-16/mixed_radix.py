"""Finite carry-aware mixed-radix cover prototype. No modulus-size enumeration
is proposed for the asymptotic algorithm; brute enumeration below is a test.
"""
from itertools import product
from collections import Counter
from functools import lru_cache
from math import prod
from pathlib import Path
import json

def positional(bases,values):
    ans=0;scale=1
    for p,x in zip(bases,values):ans+=scale*x;scale*=p
    return ans

def test(bases):
    # Different raw representatives, negative carries, repeated occurrence tags.
    choices=[[(a+p*(tag-1),b+p*(1-2*tag),tag) for a in range(p)
              for b in range(p) for tag in range(2)] for p in bases]
    Q=prod(bases);cap=2**len(bases)
    @lru_cache(None)
    def rec(i,a,b):
        if i==len(bases):return ((),)
        p=bases[i];out=[]
        for j,(l,r,tag) in enumerate(choices[i]):
            if (a-l)%p==0 and (b-r)%p==0:
                out.extend((j,)+tail for tail in rec(i+1,(a-l)//p,(b-r)//p))
        return tuple(out)
    brute={}
    for xs in product(*(range(len(C)) for C in choices)):
        left=positional(bases,[choices[i][j][0] for i,j in enumerate(xs)])
        right=positional(bases,[choices[i][j][1] for i,j in enumerate(xs)])
        key=positional(bases,[choices[i][j][1]-choices[i][j][0] for i,j in enumerate(xs)])
        assert right-left==key
        brute.setdefault((left%Q,right%Q),set()).add(xs)
    count=0
    for a in range(-2*Q,2*Q+1):
        for b in range(-2*Q,2*Q+1):
            found=rec(0,a,b)
            assert len(found)==len(set(found))
            assert 0<len(found)<=cap
            assert set(found)==brute[(a%Q,b%Q)]
            count+=1
    return {'bases':bases,'target_pairs':count,'modulus':Q,'cap':cap,
            'choice_tuples':sum(map(len,brute.values()))}

if __name__=='__main__':
    out=[test([]),test([3,5]),test([2,3,2])]
    Path(__file__).with_name('mixed_radix_results.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out,indent=2))
    print('PASS mixed-base coverage, exact congruence equivalence, signed carries, caps and output keys.')
