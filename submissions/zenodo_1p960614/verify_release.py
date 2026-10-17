"""Offline integrity check; does not run Lean or refresh online verification."""
from hashlib import sha256
from pathlib import Path, PurePosixPath
import json
import sys
import zipfile

ROOT = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def safe(name):
    p = PurePosixPath(name)
    check(not p.is_absolute() and '..' not in p.parts and '\\' not in name,
          'Unsafe path in manifest')
    return p.as_posix()


def read_json(name):
    return json.loads((ROOT / name).read_text(encoding='utf-8-sig'))


def main():
    listed = set()
    for line in (ROOT / 'SHA256SUMS.txt').read_text(encoding='utf-8').splitlines():
        expected, name = line.split('  ', 1)
        name = safe(name)
        check(name not in listed, 'Duplicate manifest entry: ' + name)
        check(digest((ROOT / name).read_bytes()) == expected, 'Hash mismatch: ' + name)
        listed.add(name)
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
              if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc'
              and p != ROOT / 'SHA256SUMS.txt'}
    check(listed == actual, 'Manifest membership mismatch: ' + str(sorted(listed ^ actual)))
    official = ROOT / 'evidence/bigospeedrun-official-final'
    hashes = read_json('evidence/bigospeedrun-official-final/source-sha256.json')
    check(len(hashes) == 689, 'Unexpected source count')
    check(len(list((ROOT / 'proof-source').rglob('*.lean'))) == 689, 'Unexpected exported source count')
    for name, expected in hashes.items():
        check(digest((ROOT / 'proof-source' / safe(name)).read_bytes()) == expected,
              'Official source mismatch: ' + name)
    audit = read_json('evidence/bigospeedrun-official-audit.json')
    check(digest((official / 'receipt.json').read_bytes()) == audit['receipt_sha256'], 'Receipt mismatch')
    check(digest((official / 'artifact.zip').read_bytes()) == audit['artifact_archive_sha256'], 'Official ZIP mismatch')
    receipt = read_json('evidence/bigospeedrun-official-final/receipt.json')
    with zipfile.ZipFile(official / 'artifact.zip') as z:
        check(z.testzip() is None, 'Official ZIP CRC failure')
        check(z.read('receipt.json') == (official / 'receipt.json').read_bytes(), 'Embedded receipt mismatch')
        for name, expected in receipt['artifact_sha256'].items():
            check(digest(z.read(name)) == expected, 'Official artifact mismatch: ' + name)
    check(receipt['status'] == 'passed', 'Receipt did not pass')
    check(receipt['request']['commit'] == '8c25c0325de5be4286413f39ca0c9278aad33f52', 'Commit mismatch')
    for line in (ROOT / 'analytic-certificate/SHA256SUMS.txt').read_text(encoding='utf-8-sig').splitlines():
        if line.strip():
            expected, name = line.split('  ', 1)
            check(digest((ROOT / 'analytic-certificate' / safe(name)).read_bytes()) == expected,
                  'Original certificate hash mismatch: ' + name)
    print(json.dumps({'integrity': 'passed', 'files_checked': len(listed),
                      'official_lean_sources_checked': len(hashes),
                      'official_artifact_members_checked': len(receipt['artifact_sha256']),
                      'lean_or_nanoda_rerun': False, 'remote_status_refreshed': False}, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, KeyError, zipfile.BadZipFile) as exc:
        print('RELEASE CHECK FAILED: ' + str(exc), file=sys.stderr)
        sys.exit(1)
