"""Build a curated, checksum-verified Zenodo upload without modifying the source archive."""
from pathlib import Path
from hashlib import sha256
from datetime import datetime, timezone
import json
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT.parents[1] / 'results/2026-10-15_1p960614'
STAGE = ROOT / 'release'
UPLOAD = ROOT / 'upload'
STAGE.mkdir(exist_ok=True)
UPLOAD.mkdir(exist_ok=True)


def copy(src, dest):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)


def run(args, cwd):
    result = subprocess.run([sys.executable, *args], cwd=cwd, capture_output=True, text=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    return result.stdout


original_check = run([str(ARCHIVE / 'verify_archive.py')], ARCHIVE)
for folder in ('proof-source', 'analytic-certificate'):
    for file in (ARCHIVE / folder).rglob('*'):
        if file.is_file() and '__pycache__' not in file.parts and file.suffix != '.pyc':
            copy(file, STAGE / file.relative_to(ARCHIVE))
for name in ('mission-completion.json', 'bigospeedrun-official-audit.json', 'bigospeedrun-anthropic-manifest.json'):
    copy(ARCHIVE / 'evidence' / name, STAGE / 'evidence' / name)
for file in (ARCHIVE / 'evidence/bigospeedrun-official-final').iterdir():
    if file.is_file():
        copy(file, STAGE / 'evidence/bigospeedrun-official-final' / file.name)
for name in ('README.txt', 'LICENSING.txt', 'verify_release.py'):
    copy(ROOT / name, STAGE / name)
copy(ROOT / 'main.tex', STAGE / 'report/main.tex')
copy(ROOT / 'build/main.pdf', STAGE / 'report/3sum-1p960614-report.pdf')
copy(ROOT / 'build/main.pdf', UPLOAD / '3sum-1p960614-report.pdf')
copy(ROOT / 'README.txt', UPLOAD / 'README.txt')
copy(ROOT / 'LICENSING.txt', UPLOAD / 'LICENSING.txt')
certlog = run(['analytic-certificate/verify_certificate.py', '--self-test'], STAGE)
(STAGE / 'evidence/release-certificate-check.txt').write_text(certlog, encoding='utf-8')
provenance = {
    'version': '1.0.0', 'packaged_at_utc': datetime.now(timezone.utc).isoformat(),
    'source_commit': '8c25c0325de5be4286413f39ca0c9278aad33f52',
    'source_url': 'https://github.com/Anchen0823/three-sum-1960614',
    'upstream_commit': '2b639655e07421b9ac743de9090459bab473a7c0',
    'author': {'name': 'Yuxuan Xu', 'orcid': '0009-0001-8760-5277', 'affiliation': 'School of Computer Science, Wuhan University'},
    'original_archive_integrity': json.loads(original_check),
    'fresh_checks': ['original archive integrity', 'exact certificates and 12 negative cases', 'curated release integrity'],
    'lean_or_nanoda_rerun': False, 'full_platform_graph_included': False,
    'licensing': 'See LICENSING.txt; no blanket license for inherited source.',
    'status': 'Prepared for author review; this file does not assert Zenodo publication.'
}
(STAGE / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
files = sorted(p for p in STAGE.rglob('*') if p.is_file() and p != STAGE / 'SHA256SUMS.txt'
               and '__pycache__' not in p.parts and p.suffix != '.pyc')
(STAGE / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(p.read_bytes()).hexdigest()}  {p.relative_to(STAGE).as_posix()}\n' for p in files), encoding='utf-8')
integrity = run(['verify_release.py'], STAGE)
(ROOT / 'release-validation.json').write_text(integrity, encoding='utf-8')
target = UPLOAD / '3sum-1p960614-artifact-v1.0.0.zip'
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for p in files + [STAGE / 'SHA256SUMS.txt']:
        z.write(p, p.relative_to(STAGE).as_posix())
with zipfile.ZipFile(target) as z:
    assert z.testzip() is None
uploaded = sorted(p for p in UPLOAD.iterdir() if p.is_file() and p.name != 'SHA256SUMS.txt')
(UPLOAD / 'SHA256SUMS.txt').write_text(''.join(f'{sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in uploaded), encoding='utf-8')
print(integrity)
print(json.dumps({p.name: p.stat().st_size for p in sorted(UPLOAD.iterdir()) if p.is_file()}, indent=2))
