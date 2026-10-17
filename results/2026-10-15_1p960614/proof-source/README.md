# Deterministic word-RAM 3SUM at exponent 1.960614

The entry point is `Race.bound` in `Submission.lean`, with exact rational bound
980307/500000 and the unchanged official `EndStatement.ThreeSum` specification.
The official verifier supplies Lean 4.33.1 and its pinned Mathlib environment.

The machine proof extends c0ldzy17/three-sum-lean at commit
2b639655e07421b9ac743de9090459bab473a7c0 with expansion 232, the author-supplied
3sum_certificate_1p960614_v3 quartic and parameters, exact integer schedules,
and changed execution, cost and resource proofs. Codex assisted the extension.
Inherited Anthropic and other source credits, license headers and notices are
retained. See LICENSE and NOTICE. The independent fixed-model lower bound is
not used as an algorithmic premise.

Package preparation and a local Lean build do not establish site acceptance.
Comparator must independently compare the full theorem and definitions with
the official frozen statement, and the allowed-axiom audit must pass.
