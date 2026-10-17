Deterministic Integer 3SUM at Exponent 1.960614
Quartic Switch Certificates and a Lean Word-RAM Proof
Version 1.0.0 -- 2026-10-15

Author: Yuxuan Xu
Affiliation: School of Computer Science, Wuhan University
ORCID: https://orcid.org/0009-0001-8760-5277

Read 3sum-1p960614-report.pdf first. This is a technical report and formal
proof artifact, not a journal article or an assertion of human peer review.
The result concerns polynomially bounded integer 3SUM in the precise
deterministic word-RAM model of proof-source/Submission/EndStatement.lean.
The exact endpoint is EndStatement.ThreeSum.SolvedInTime (980307/500000 : Rat).

Files in the accompanying archive:
  report/                PDF and standalone LaTeX source
  proof-source/          unchanged pinned native source: 693 files, 689 Lean files
  analytic-certificate/  original exact rational certificates, checker, notes
  evidence/              selected official verification and completion records
  provenance.json        source/version pins and limits of this package
  LICENSING.txt          per-component license scope
  verify_release.py      offline integrity checker
  SHA256SUMS.txt          checksums of all archived files except itself

QUICK CHECK (Python 3.10+, standard library only)
  python verify_release.py
  python analytic-certificate/verify_certificate.py --self-test

The first command checks bytes, the official 689-source hash map, and the
official verifier artifact. It is not a new Lean proof check. The second
checks 3 exact certificates and rejection of 12 intentionally corrupted
certificates. The older analytic README correctly describes that package's
own scope: arithmetic certificates alone do not prove a complete program.
The subsequent machine proof and archived official receipt are separate.

FULL FORMAL REPRODUCTION
  Source: https://github.com/Anchen0823/three-sum-1960614
  Commit: 8c25c0325de5be4286413f39ca0c9278aad33f52
  Entry: Submission.lean / Race.bound
  Lean: leanprover/lean4:v4.33.1
  Mathlib: 0df444a360eaa60ab8c11dca51a86af692955474
  Verifier: https://github.com/bigospeedrun/verifier
  Verifier commit: 51489ee2ac82596a41375e92ea8108814f931242
  Official run: https://github.com/bigospeedrun/verifier/actions/runs/38567645711
  Dependency lock: evidence/bigospeedrun-anthropic-manifest.json

Use the pinned official verifier environment and its submission/profile
workflow, including statement comparison, axiom audit, Lean, and Nanoda.
The submission layout deliberately has no independent Lake configuration:
the verifier supplies it. Merely invoking lake build in an unrelated
workspace does not reproduce this theorem. The receipt and original
artifact.zip preserve the exact official checks and logs.

The platform completion receipt is preserved for provenance. This curated
deposit does not include every Prove2Me graph response or platform export
referenced by that receipt. Its graph counts are not independently
reconstructed by verify_release.py. The authoritative native proof source
and official verification artifact are included in full.

This release excludes later unfinished exponent improvements. Its
preparation reran integrity and rational certificate checks, not full Lean
or Nanoda. It makes no new speedrun eligibility or priority adjudication.

ATTRIBUTION
The extension builds on c0ldzy17/three-sum-lean at commit
2b639655e07421b9ac743de9090459bab473a7c0 and its cited upstream lineage,
including Alman and Vassilevska Williams and Anthropic formalizations.
OpenAI Codex assisted formalization, artifact preparation, and this report.
See the report's attribution section and the preserved original notices.
