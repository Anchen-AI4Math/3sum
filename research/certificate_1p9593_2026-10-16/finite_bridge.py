"""Finite integration checks for the new arithmetic / mass / reporting bridge.

Standard library only. Tiny hash covers are witnesses for finite tests, not the
large-n exhaustive greedy construction or a performance implementation.
"""
from collections import Counter
from functools import lru_cache
from itertools import combinations, product, permutations
from math import prod
import json, random


def require(ok, message):
    if not ok:
        raise ValueError(message)


def joint(q, p):
    return q if q % p == 0 else q*p


def differences(A, B, C):
    return [c-b-a for a, b, c in product(A, B, C)]


def weighted_score(ds, pool, q):
    return sum(sum(z % p != 0 for p in pool) for z in ds if z % q == 0)


def count_score(ds, pool, q):
    count = lambda m: sum(z % m == 0 for z in ds)
    return len(pool)*count(q)-sum(count(joint(q, p)) for p in pool)


def chain(ds, pool, depth, y):
    q = 1
    zmax = max([1]+[abs(z) for z in ds])
    K = 0
    while y**(K+1) <= zmax:
        K += 1
    trace = []
    for _ in range(depth):
        scores = [(count_score(ds, pool, q*p), p) for p in pool]
        after, chosen = min(scores)
        before = weighted_score(ds, pool, q)
        require(len(pool)*after <= K*before, 'contraction')
        require(all(v == weighted_score(ds, pool, q*p) for v, p in scores),
                'score implementation')
        trace.append([q, chosen, before, after])
        q *= chosen
    return q, trace


def covers(L, p, seed):
    """Deterministic tiny witnessed covers, independently check every residue pair."""
    rng = random.Random(seed)
    missing = set(product(range(p), repeat=2))
    rows = []
    for _ in range(10000):
        weights = [(rng.randrange(p), rng.randrange(p)) for _ in range(L)]
        left = [sum(weights[i][int(i == j)] for i in range(L)) for j in range(L)]
        right = [sum(weights[i][int(i != j)] for i in range(L)) for j in range(L)]
        cap = (4*(p+L)+p-1)//p
        lc, rc = Counter(x % p for x in left), Counter(x % p for x in right)
        keepL = [lc[x % p] <= cap for x in left]
        keepR = [rc[x % p] <= cap for x in right]
        hits = {(left[i] % p, right[j] % p) for i in range(L) for j in range(L)
                if i != j and keepL[i] and keepR[j]}
        if hits & missing:
            rows.append((left, right, keepL, keepR))
            missing -= hits
        if not missing:
            return rows, cap
    raise ValueError('tiny cover construction did not finish')


def subsets(mask):
    original = mask
    while True:
        yield mask
        if not mask:
            return
        mask = (mask-1) & original


def mask_layer(positions, k):
    return [sum(1 << i for i in xs) for xs in combinations(positions, k)]


def integration_fixture():
    lengths, radices = (4, 6), (7, 11)
    blocks = [list(range(4)), list(range(4, 10))]
    local = [covers(L, p, 100+L) for L, p in zip(lengths, radices)]
    cap = prod(len(rows)*B*B for rows, B in local)
    Q = prod(radices)
    down = [a | b for a in [0]+mask_layer(blocks[0], 1)+mask_layer(blocks[0], 2)
            for b in [0]+mask_layer(blocks[1], 1)+mask_layer(blocks[1], 2)]
    output_masks = [a | b for a, b in product(mask_layer(blocks[0], 2), mask_layer(blocks[1], 2))]
    fixtures = []
    counts = Counter()
    for row0, row1 in product(*(x[0] for x in local)):
        endpoints = {}
        for i, j in product(range(4), range(6)):
            m = (1 << i) | (1 << (4+j))
            endpoints[m] = (row0[0][i]+7*row1[0][j], row0[1][i]+7*row1[1][j],
                            row0[2][i] and row1[2][j], row0[3][i] and row1[3][j])
        keys = {}
        for out in output_masks:
            for a in subsets(out):
                b = out ^ a
                if a in endpoints and b in endpoints:
                    key = endpoints[b][1]-endpoints[a][0]
                    if out in keys:
                        require(keys[out] == key, 'key depends on internal partition')
                    keys[out] = key
                    if endpoints[a][2] and endpoints[b][3]:
                        counts[endpoints[a][0] % Q, endpoints[b][1] % Q] += 1
        fixtures.append((endpoints, keys))
    require(len(counts) == Q*Q, 'mixed radix has an uncovered target')
    require(max(counts.values()) <= cap, 'representation bound')
    return Q, cap, down, fixtures, dict(local_cover_lengths=[len(x[0]) for x in local],
                                      target_pairs=Q*Q, representation_cap=cap,
                                      actual_max_representations=max(counts.values()))


def run_integrated(A, B, C, Q, cap, down, fixtures):
    """One owner, all literal key records, duplicate input positions retained."""
    pool = [3, 5, 7, 11]
    ds = differences(A, B, C)
    P, prime_trace = chain(ds, pool, 1, 3)
    require(prod(pool) > max([0]+[abs(x) for x in ds]), 'auxiliary coverage')
    H = weighted_score(ds, pool, P)
    false = sum(z != 0 and z % P == 0 for z in ds)
    require(false <= H and H == count_score(ds, pool, P), 'false mass')
    require(4*P <= Q, 'guarded modulus')
    left = [(i, j, a % P+j*P) for i, a in enumerate(A) for j in (-1, 0, 1)]
    kh = Counter(key % Q for _, keys in fixtures for key in keys.values())
    scores = [sum(kh[(v+d) % Q] for _, _, v in left) for d in range(Q)]
    d = min(range(Q), key=lambda t: (scores[t], t))
    output_count = sum(len(keys) for _, keys in fixtures)
    require(Q*scores[d] <= len(left)*output_count, 'offset averaging')
    Bpop, Cpop = Counter(b % P for b in B), Counter((c % P+d) % Q for c in C)
    threshold = cap*H
    mass = 0
    wanted = 0
    terminals = 0
    found = False
    guard = False
    # First pass computes every root mass before reporting, as in PROOF.txt.
    positive = []
    tables = {}
    for fi, (endpoints, keys) in enumerate(fixtures):
        f = {m: Bpop[l % Q] if kl else 0 for m, (l, r, kl, kr) in endpoints.items()}
        g = {m: Cpop[r % Q] if kr else 0 for m, (l, r, kl, kr) in endpoints.items()}
        F = {m: f.get(m, 0) for m in down}
        G = {m: g.get(m, 0) for m in down}
        for bit in range(10):
            for m in down:
                if m >> bit & 1:
                    F[m] += F[m ^ (1 << bit)]
                    G[m] += G[m ^ (1 << bit)]
        tables[fi] = (F, G)

        def weight(m):
            return (-1)**(4-m.bit_count())*F[m]*G[m]

        @lru_cache(None)
        def box(flags, e):
            if not e:
                return weight(flags)
            xs = [i for i in range(10) if flags >> i & 1]
            bit = 1 << xs[e-1]
            return box(flags, e-1)+box(flags ^ bit, e-1)

        for out, key in keys.items():
            for ai, lift, value in left:
                if (key-value-d) % Q:
                    continue
                wanted += 1
                # Sparse cut k=1: one direct leaf and four disjoint boxes.
                root = weight(out)
                for bit in [i for i in range(10) if out >> i & 1]:
                    flags = out ^ (1 << bit)
                    free = flags & ((1 << bit)-1)
                    root += box(flags, free.bit_count())
                direct = sum(f.get(a, 0)*g.get(out ^ a, 0) for a in subsets(out))
                require(root == direct and root >= 0, 'root query mismatch')
                mass += root
                if mass > threshold:
                    guard = True
                    break
                if root:
                    positive.append((fi, ai, out, root))
            if guard:
                break
        if guard:
            break
    if not guard:
        require(wanted == scores[d], 'literal wanted enumeration')
        require(len(positive) <= mass <= threshold, 'frontier mass')
        for fi, ai, out, root in positive:
            endpoints = fixtures[fi][0]
            F, G = tables[fi]
            leaf_mass = 0
            child_total = 0
            child_positive = 0
            first, suffix = out & 15, out & ~15
            # Exact conditional prefix queries before terminal suffix enumeration.
            for bit0 in [i for i in range(4) if first >> i & 1]:
                ap = 1 << bit0
                bp = first ^ ap
                child = sum((-1)**(2-x.bit_count())*F[ap | x]*G[bp | x]
                            for x in subsets(suffix))
                require(child >= 0, 'negative conditional query')
                child_total += child
                if not child:
                    continue
                child_positive += 1
                child_leaves = 0
                for bit1 in [i for i in range(4, 10) if suffix >> i & 1]:
                    a = ap | (1 << bit1)
                    b = out ^ a
                    l, _, kl, _ = endpoints[a]
                    _, r, _, kr = endpoints[b]
                    if not (kl and kr):
                        continue
                    bs = [v for v in B if v % P == l % Q]
                    cs = [v for v in C if (v % P+d) % Q == r % Q]
                    child_leaves += len(bs)*len(cs)
                    for bv, cv in product(bs, cs):
                        terminals += 1
                        require((cv-bv-A[ai]) % P == 0, 'unsound modular lift')
                        found |= cv-bv-A[ai] == 0
                require(child_leaves == child, 'conditional terminal mass')
                leaf_mass += child_leaves
            require(child_total == root and child_positive <= root, 'prefix conservation')
            require(leaf_mass == root, 'terminal mass not conserved')
        require(terminals == mass, 'cumulative terminal accounting')
    truth = any(z == 0 for z in ds)
    require((guard or found) == truth, 'wrong 3SUM decision')
    return dict(A=A, B=B, C=C, truth=truth, guard=guard, shift=d,
                chosen_modulus=P, prime_trace=prime_trace,
                false_triples=false, weighted_score=H, threshold=threshold,
                scanned_mass=mass, wanted_scanned=wanted, candidate_checks=terminals)


def band_catalog(A, B, C, g):
    arrays = [sorted(set(a)) for a in (A, B, C)]
    bands = [[a[i:i+g] for i in range(0, len(a), g)] for a in arrays]
    aa, bb, cc = bands
    lookup = lambda xs, v: next((i for i, a in enumerate(xs) if a[0] <= v <= a[-1]), None)
    records = []
    for j, b in enumerate(bb):
        for k, c in enumerate(cc):
            i = lookup(aa, c[0]-b[-1])
            if i is not None:
                records.append((i, j, k))
    for i, a in enumerate(aa):
        for j, b in enumerate(bb):
            k = lookup(cc, a[0]+b[0])
            if k is not None:
                records.append((i, j, k))
        for k, c in enumerate(cc):
            j = lookup(bb, c[0]-a[0])
            if j is not None:
                records.append((i, j, k))
    relevant = {(i, j, k) for i, a in enumerate(aa) for j, b in enumerate(bb)
                for k, c in enumerate(cc) if a[0]+b[0] <= c[-1] and c[0] <= a[-1]+b[-1]}
    require(set(records) == relevant, 'band owner catalog')
    require(len(records) <= len(aa)*len(bb)+len(aa)*len(cc)+len(bb)*len(cc), 'owner bound')
    return bands, records


def original_index_checks():
    cases = [[0], [0, 0], [0, 0, 0], [-1, -1, 2], [-3, 1, 2, 4],
             [1, 2, 4, 8], [-5, -2, 0, 2, 5, 5]]
    checked = 0
    for values in cases:
        n = len(values)
        truth = any(sum(values[i] for i in ids) == 0 for ids in combinations(range(n), 3))
        bits = max(1, (n-1).bit_length())
        found = False
        for b0, b1 in product(range(bits), repeat=2):
            patterns = [((i >> b0) & 1)+2*((i >> b1) & 1) for i in range(n)]
            for selected in permutations(range(4), 3):
                classes = [[values[i] for i in range(n) if patterns[i] == pattern]
                           for pattern in selected]
                A, B, negC = classes
                C = [-x for x in negC]
                for g in (1, 2):
                    bands, records = band_catalog(A, B, C, g)
                    for i, j, k in records:
                        found |= any(a+b == c for a, b, c in product(bands[0][i], bands[1][j], bands[2][k]))
                    checked += 1
        require(found == truth, 'original-index coloring and band reduction')
    return dict(input_cases=len(cases), colored_band_catalogs=checked)


def run():
    score_cases = 0
    chain_traces = []
    for A, B, C in [([0, 0], [0, 1], [0, 1]), ([-7, 2], [-3, 4], [-10, 5]),
                    ([1, 2], [3, 4], [9, 11])]:
        ds = differences(A, B, C)
        for q in range(1, 41):
            require(weighted_score(ds, [2, 3, 5, 7], q) == count_score(ds, [2, 3, 5, 7], q),
                    'shared-factor weighted score')
            score_cases += 1
        _, trace = chain(ds, [3, 5, 7], 4, 3)
        chain_traces.append(trace)
    lifts = 0
    for P in range(1, 9):
        for Q in [4*P, 4*P+1, 6*P+3]:
            for a, b, c in product(range(P), repeat=3):
                matches = [j for j in (-1, 0, 1) if (c-b-a-j*P) % Q == 0]
                require(len(matches) <= 1, 'nonunique lift')
                require(bool(matches) == ((c-b-a) % P == 0), 'lift equivalence')
                for j in matches:
                    require(c-b-a == j*P, 'guarded lift equality')
                lifts += 1
    # Negative tests demonstrate why the hypotheses are needed.
    require(joint(6, 3) != 18, 'negative shared-factor example')
    require(count_score([6], [2, 3], 6) !=
            2-sum(6 % (6*p) == 0 for p in [2, 3]), 'naive q*p score should fail')
    require((-2-2) % 4 == 0 and -2 != 2,
            'missing 4P guard counterexample')
    Q, cap, down, fixtures, meta = integration_fixture()
    cases = [([0, 0], [0, 0], [0, 0]), ([-1, 1], [-2, 2], [-3, 3]),
             ([0], [0], [1]), ([0], [0], [3, 5, 7, 11]),
             ([0, 0], [0, 0], [0, 3, 5, 7, 11]), ([1, 1], [2, 2], [3, 8]),
             ([-4, 2], [-1, 3], [-5, 6])]
    integrations = [run_integrated(*case, Q, cap, down, fixtures) for case in cases]
    require(any(x['guard'] for x in integrations), 'YES guard never exercised')
    require(any(x['truth'] and not x['guard'] for x in integrations), 'ordinary YES path untested')
    require(any(not x['truth'] and x['false_triples'] for x in integrations), 'false positives untested')
    return dict(status='PASS finite integration checks; not an asymptotic runtime test',
                score_cases=score_cases, guarded_lift_cases=lifts, chain_traces=chain_traces,
                mixed_cover=meta, integrations=integrations, original_indices=original_index_checks(),
                negative_examples=3)


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))
