"""Package manuscript separately from reproducibility material; no network writes."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import json
import shutil

dest = Path(__file__).resolve().parent
root = dest.parent.parent
original = root / 'research/3sum_exponent_research_2026-10-13'
pdf = dest / 'build' / 'main.pdf'
compile_result = json.loads((dest / 'build' / 'compile_result.json').read_text(encoding='utf-8-sig'))
if (not pdf.is_file() or compile_result.get('exitCode') != 0
        or pdf.stat().st_mtime < (dest / 'main.tex').stat().st_mtime):
    raise SystemExit('Missing successfully compiled PDF; packaging stopped.')
shutil.copy2(pdf, dest / 'main.pdf')
with ZipFile(dest / 'hexagon_source.zip', 'w', ZIP_DEFLATED) as z:
    z.write(dest / 'main.tex', 'main.tex')

reproduce = '''from pathlib import Path
import subprocess
import sys
root = Path(__file__).resolve().parent
for script in [root / "research/3sum_exponent_research_2026-10-13/3sum-research/verify_exponents.py", root / "audit/independent_audit.py"]:
    subprocess.run([sys.executable, str(script)], cwd=root, check=True)
print("Reproduction complete. No Lean build performed.")
'''
with ZipFile(dest / 'verification_bundle.zip', 'w', ZIP_DEFLATED) as z:
    for path in sorted(original.rglob('*')):
        if path.is_file() and '__pycache__' not in path.parts:
            z.write(path, path.relative_to(root).as_posix())
    for name in ['archives/3sum_exponent_research_2026-10-13.zip',
                 'audit/independent_audit.py', 'audit/independent_audit_output.txt',
                 'audit/AUDIT_REPORT_2026-10-13.txt']:
        z.write(root / name, name)
    z.writestr('reproduce.py', reproduce)
    if (dest / 'build' / 'fresh_verification.txt').is_file():
        z.write(dest / 'build' / 'fresh_verification.txt', 'fresh_verification.txt')
    z.writestr('README.txt', 'Run: python reproduce.py\n'
               'This archive is supplementary local reproducibility material, not the Hexagon source upload.\n'
               'The original verifier is unchanged. The independent checker includes archive integrity checks.\n'
               'No complete Lean certification is included.\n')

names = ['main.tex', 'main.pdf', 'hexagon_source.zip', 'verification_bundle.zip',
         'FORM_CONTENT.txt', 'README_提交说明.txt']
lines = []
for name in names:
    path = dest / name
    lines.append(f'{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}')
(dest / 'MANIFEST.sha256').write_text('\n'.join(lines)+'\n', encoding='utf-8')
with ZipFile(dest / 'hexagon_source.zip') as z:
    assert z.namelist() == ['main.tex']
    assert z.read('main.tex') == (dest / 'main.tex').read_bytes()
print(json.dumps({'packaged_files': names, 'source_archive_entry_point': 'main.tex',
                  'uploaded': False}, indent=2, ensure_ascii=False))
