"""Executable heterogeneous capped-lattice core; compares to direct counting.

This is a query/encoding primitive, not a complete asymptotic 3SUM solver.
All counts are exact integers; inputs deliberately include repeated populations.
"""
from itertools import combinations,product
from functools import lru_cache
import json,random
from pathlib import Path

def layer(positions,k):
    return [sum(1<<i for i in cc) for cc in combinations(positions,k)]
def subsets(mask):
    s=mask
    while True:
        yield s
        if not s:break
        s=(s-1)&mask

def run(lengths=(6,10),seed=1729):
    blocks=[];start=0
    for L in lengths:blocks.append(list(range(start,start+L)));start+=L
    endpoints=[sum(p) for p in product(*(layer(b,1) for b in blocks))]
    outputs=[sum(p) for p in product(*(layer(b,2) for b in blocks))]
    down=[sum(p) for p in product(*([0]+layer(b,1)+layer(b,2) for b in blocks))]
    rng=random.Random(seed)
    f={s:rng.randrange(5) for s in endpoints};g={s:rng.randrange(5) for s in endpoints}
    def zeta(values):
        out={s:values.get(s,0) for s in down}
        for i in range(start):
            for s in down:
                if s>>i&1:out[s]+=out[s^(1<<i)]
        return out
    F=zeta(f);G=zeta(g)
    for x in down:
        assert F[x]==sum(f.get(s,0) for s in subsets(x))
        assert G[x]==sum(g.get(s,0) for s in subsets(x))
    cases=0;lookups=0;visited_boxes=0
    # Prefix conditioning implements the reporting query after fixing earlier blocks.
    for depth in range(len(blocks)):
        suffix=blocks[depth:];r=2*len(suffix)
        prefix_rows=[(0,0)]
        for b in blocks[:depth]:
            prefix_rows=[(pl|l,pr|(q^l)) for pl,pr in prefix_rows
                         for q in layer(b,2) for l in layer(b,1) if l&q==l]
        suffix_outputs=[sum(p) for p in product(*(layer(b,2) for b in suffix))]
        for pl,pr in prefix_rows:
            def weight(s):return (-1)**(r-s.bit_count())*F[pl|s]*G[pr|s]
            @lru_cache(None)
            def box(flags,e):
                # Canonical free set consists of e smallest flagged coordinates.
                pos=[i for i in range(start) if flags>>i&1]
                if e==0:return weight(flags)
                x=1<<pos[e-1]
                return box(flags,e-1)+box(flags^x,e-1)
            for q in suffix_outputs:
                expected=sum(f.get(pl|s,0)*g.get(pr|(q^s),0) for s in subsets(q))
                pos=[i for i in range(start) if q>>i&1]
                for cut in range(r//2+1):
                    got=0;partition=[]
                    for m in range(cut):
                        for missing in layer(pos,m):
                            got+=weight(q^missing);partition.append(q^missing);lookups+=1
                    for missing in layer(pos,cut):
                        flags=q^missing
                        free=flags if cut==0 else flags&((1<<min(i for i in pos if missing>>i&1))-1)
                        got+=box(flags,free.bit_count());visited_boxes+=1
                        partition.extend(s for s in subsets(flags) if s&(flags^free)==flags^free)
                    assert len(partition)==2**r and set(partition)==set(subsets(q))
                    assert got==expected,(lengths,depth,pl,pr,q,cut,got,expected)
                    cases+=1
    return dict(lengths=lengths,seed=seed,endpoint_coordinates=len(endpoints),
                full_output_coordinates=len(outputs),capped_zeta_coordinates=len(down),
                exact_queries=cases,direct_leaf_reads=lookups,box_reads=visited_boxes)

if __name__=='__main__':
    results=[run((6,10),1729),run((10,6),2718)]
    print(json.dumps(results,indent=2))
    Path(__file__).with_name('finite_core_results.json').write_text(json.dumps(results,indent=2)+'\n')
    print('PASS all heterogeneous zeta, sparse-box, prefix and weighted-count checks.')
