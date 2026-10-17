"""Offline reproduction of the fixed 1.9593 certificate, Python standard library.

Exact numeric proofs + finite implementation checks + file integrity. This does
not compile or validate a Lean end-to-end runtime theorem. PROOF.txt is separate.
"""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, copy, sys
import verify_numeric
import finite_core
import mixed_radix
import finite_bridge

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def fixed(data):
    require(data['expansions'] == [72, 252], 'wrong fixed expansion profile')
    expected = dict(epsilon='0.215745630', beta='-0.046171284', saving='0.189008426',
                    split='0.340200365', tau='0.65', principal='1.95925', target='1.9593')
    require(set(data['parameters']) == set(expected), 'wrong fixed parameter fields')
    for key, value in expected.items():
        require(type(data['parameters'][key]) in (str, int), 'non-exact fixed parameter')
        require(F(data['parameters'][key]) == F(value), 'wrong fixed parameter: '+key)
    return verify_numeric.verify(data, False)


def integrity():
    manifest = json.loads((ROOT/'MANIFEST.json').read_text(encoding='utf-8'))
    for name, expected in manifest['sha256'].items():
        path = (ROOT/name).resolve()
        require(path.is_relative_to(ROOT), 'manifest path escapes package')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected,
                'integrity mismatch: '+name)
    return len(manifest['sha256'])


def run():
    require(not sys.flags.optimize, 'run without -O: finite tests use Python assertions')
    files = integrity()
    print('PASS package integrity:', files, 'files', flush=True)
    data = json.loads((ROOT/'certificate.json').read_text(encoding='utf-8'))
    numeric = fixed(data)
    print('PASS exact continuum, twelve costs, and finite rounding thresholds', flush=True)
    verify_numeric.negative_tests(data)
    for field, replacement in [('target', '1.9592'), ('saving', 0.189008426)]:
        forged = copy.deepcopy(data)
        forged['parameters'][field] = replacement
        try:
            fixed(forged)
        except ValueError:
            print('PASS rejection: wrong fixed '+field, flush=True)
        else:
            raise ValueError('accepted a forged fixed certificate')
    core = [finite_core.run((6, 10), 1729), finite_core.run((10, 6), 2718)]
    print('PASS heterogeneous weighted core:', sum(x['exact_queries'] for x in core), flush=True)
    radix = [mixed_radix.test([]), mixed_radix.test([3, 5]), mixed_radix.test([2, 3, 2])]
    print('PASS signed / repeated mixed radix:', sum(x['target_pairs'] for x in radix), flush=True)
    bridge = finite_bridge.run()
    print('PASS original-input reductions, prime chain, offsets, guards, and terminal checking', flush=True)
    result = dict(target='1.9593', status='PASS EXACT CERTIFICATE AND FINITE CHECKS',
                  proof_status='Paper algorithm proof in PROOF.txt; NOT a Lean machine theorem',
                  integrity_files=files, numeric=numeric, numeric_negative_tests=6,
                  core=core, mixed_radix=radix, bridge=bridge)
    (ROOT/'RESULTS.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print('Saved RESULTS.json. Finite tests do not establish asymptotic runtime.', flush=True)
    return result


if __name__ == '__main__':
    run()
