"""Independent numerical ledger and finite identity checks; not a Lean rebuild."""
import itertools, json, math
from fractions import Fraction
from pathlib import Path

pi = [.81204903, .15860350, .02934747]
alpha = [.90113327, .08908424, .00978249]
delta, y, z = .01344845, .18162395, .07523953
entropy = lambda p: -sum(x * math.log2(x) for x in p if x)
H, A = entropy(pi), entropy(alpha)
G = pi[1] + pi[2] * math.log2(3)
B = math.log2(1+y+y*y) - (pi[1]+2*pi[2]-delta)*math.log2(y)
Q = pi[1]*math.log2(1+z)+pi[2]*math.log2(1+z+z*z)-delta*math.log2(z)
ledger = dict(bank=2*B/H, query=2-G/H+2*Q/H, endpoint=2*A/H,
              histogram=1+G/H, incidence=2-G/H, linear=1)
assert max(ledger.values()) < 1.9203

def choose(n,k):
    return math.comb(n,k) if k <= n else 0

# Exact integer check: top-rank binomial inversion with factorial weights.
checks = 0
for N in range(1,4):
    words = list(itertools.product(range(3), repeat=N))
    for a in words:
        for b in words:
            for q in words:
                if sum(a)+sum(b) != sum(q):
                    continue
                coef = math.prod(sum((-1)**(qi-r)*choose(qi,r)*choose(r,ai)*choose(r,bi)
                                     for r in range(qi+1))
                                 for ai,bi,qi in zip(a,b,q))
                lhs = coef * math.prod(math.factorial(v) for v in a+b)
                rhs = math.prod(math.factorial(v) for v in q) if all(ai+bi==qi for ai,bi,qi in zip(a,b,q)) else 0
                assert lhs == rhs
                checks += 1

def exact_rank(matrix):
    a = [[Fraction(v) for v in row] for row in matrix]
    r = 0
    for c in range(len(a[0])):
        pivot = next((i for i in range(r,len(a)) if a[i][c]),None)
        if pivot is None:
            continue
        a[r],a[pivot] = a[pivot],a[r]
        v = a[r][c]
        a[r] = [x/v for x in a[r]]
        for i in range(len(a)):
            if i != r:
                v = a[i][c]
                a[i] = [x-v*y for x,y in zip(a[i],a[r])]
        r += 1
    return r

joint_dimensions = []
for alphabet in (3,4,5):
    cells = [(a,b) for a in range(alphabet) for b in range(alphabet) if a+b<alphabet]
    matrix = [[int(a==k) for a,b in cells] for k in range(alphabet)]
    matrix += [[int(b==k) for a,b in cells] for k in range(alphabet)]
    matrix += [[int(a+b==k) for a,b in cells] for k in range(alphabet)]
    r = exact_rank(matrix)
    joint_dimensions.append(dict(alphabet=alphabet,cells=len(cells),rank=r,free=len(cells)-r))

result = dict(scope='Numerical ledger and finite identities only; no full algorithm or Lean rebuild',
              entropy=dict(H=H,A=A,G=G,B=B,Q=Q), ledger=ledger,
              exact_top_rank_cases=checks, joint_type_dimensions=joint_dimensions,
              principal_certificate=1.9203, runtime_envelope=1.9209, exported_exponent=1.921)
Path(__file__).with_name('checks.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
