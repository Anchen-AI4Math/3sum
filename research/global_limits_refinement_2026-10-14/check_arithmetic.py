"""Cross-check the fast rigorous intervals against the inherited implementation."""
from pathlib import Path
from fractions import Fraction as F
import random,json
from fast_rational import log2
from exact_interval import log_iv
ROOT=Path(__file__).resolve().parent

if __name__=='__main__':
    rng=random.Random(20261014)
    for _ in range(120):
        x=F(rng.randint(1,1000000),rng.randint(1,1000000))
        fast=log2(x);full=log_iv(x)/log_iv(2)
        assert fast.lo<=full.lo<=full.hi<=fast.hi
    result={'cases':120,'seed':20261014,'status':'PASS exact containment of inherited 48-term log intervals'}
    (ROOT/'arithmetic_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'])
