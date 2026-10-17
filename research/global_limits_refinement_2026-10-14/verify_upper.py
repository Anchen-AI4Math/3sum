"""Reuse the already audited arbitrary-segment exact upper-bound checker."""
from pathlib import Path
import importlib.util,json,argparse
ROOT=Path(__file__).resolve().parent
prior=ROOT.parent/'heterogeneous_limits_2026-10-14/verify_profile.py'
spec=importlib.util.spec_from_file_location('prior_profile_verifier',prior)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
F=module.F;floor_dec=module.floor_dec;ceil_dec=module.ceil_dec
dual=module.dual;weights=module.weights;verify=module.verify

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--self-test',action='store_true');args=ap.parse_args()
    data=json.loads((ROOT/'upper_certificate.json').read_text());out=verify(data)
    if args.self_test:module.negative_tests(data)
    (ROOT/'upper_verification.json').write_text(json.dumps(out,indent=2)+'\n')
