"""Independent arithmetic and finite checks; does not import the submitted verifier.

Decimal computations are numerical cross-checks, not interval certificates.
The binomial entropy and geometric-tail finite checks use exact integers.
"""
from decimal import Decimal as D, getcontext
from math import comb
from pathlib import Path
from zipfile import ZipFile

getcontext().prec = 90
root = Path(__file__).resolve().parent.parent

def H(x):
    return -x*x.ln()-(1-x)*(1-x).ln()

for label, c, theta, a, s, target in [
    ('A', 22, '0.11229', '0.05405', '0.06862', '1.999073'),
    ('B', 21, '0.11202', '0.05665', '0.06945', '1.999017'),
]:
    c, theta, a, s, target = map(D, (c, theta, a, s, target))
    old = theta*((c-1)/9).ln()/D(4).ln()
    sharp = (c*H(1/c)-c*H((1-theta)/c)-theta*D(9).ln())/D(4).ln()
    gamma = old if label == 'A' else sharp
    q = (H(theta)+theta*D(9).ln())/D(4).ln()
    A = (c*D(10).ln()-c*H(1/c)/2-(c-1)*D(3).ln())/D(4).ln()
    B = (c*H(1/c)/2+(c-1)*D(3).ln())/D(4).ln()
    margins = [gamma-s, D('.5')-q-s, 1-a*(A+gamma), A-B,
               3-a*s/2-D(7).ln()/D(2).ln()-D('1.5')*a,
               3-a*s/2-(2+a*(1+s/2)), target-(2-a*s/4),
               1-a, D('.5')-s/2, sharp-old]
    assert all(x > 0 for x in margins)
    print(f'{label}: independent Decimal checks PASS; cutoff={2-a*s/4}; gap={margins[6]}')

# exp(r H(k/r)) = r^r / (k^k (r-k)^(r-k)); includes k=0,r with 0^0=1.
count = 0
for r in range(1, 101):
    for k in range(r+1):
        den = k**k * (r-k)**(r-k)
        value = comb(r, k)*den
        assert value <= r**r <= (r+1)*value
        count += 1
print(f'Exact binomial entropy bounds: PASS ({count} pairs, r=1..100, all k).')

count = 0
for c in (11, 12, 21, 22, 30):
    for m in range(1, 81):
        L = c*m
        tail = 0
        for t in range(m, -1, -1):
            beta = comb(L, m-t)*9**(L-m+t)
            tail += beta
            assert tail*(c-10) <= beta*(c-1)
            assert tail*(L-m+1-9*m) <= beta*(L-m+1)
            count += 1
print(f'Exact geometric tail bounds: PASS ({count} triples, including t=0,m).')

# Direct finite check of the complete sharp entropy-tail estimate in log space.
theta = D('0.11202')
c = 21
rate = c*H(D(1)/c)-c*H((1-theta)/c)-theta*D(9).ln()
for m in list(range(1, 101)) + [200, 500, 1000]:
    t = (5601*m+49999)//50000
    L = c*m
    # Cancel the common factor 9^(L-m) before forming integers.
    tail = sum(comb(L, m-d)*9**d for d in range(t, m+1))
    lhs = D(tail).ln()-D(comb(L, m)).ln()
    rhs = (D(20)/11).ln()+D(21*m+1).ln()-m*rate
    assert lhs <= rhs
print('Full sharp-tail bound: Decimal cross-check PASS for m=1..100,200,500,1000.')

with ZipFile(root/'archives/3sum_exponent_research_2026-10-13.zip') as z:
    checked = 0
    for name in z.namelist():
        if not name.endswith('/'):
            local = root/'research/3sum_exponent_research_2026-10-13'/name
            assert local.read_bytes() == z.read(name), name
            checked += 1
print(f'Archive vs extracted files: byte-identical ({checked} files).')
print('These checks do not build Lean or certify a complete word-RAM program.')
