import Submission.ThreeSum.AnalysisDefinitions

set_option autoImplicit false
set_option relaxedAutoImplicit false

/-!
Executable natural-number schedules from PROOF.md, Section 4.1.
The even microblock construction follows c0ldzy17/three-sum-lean,
Submission/ThreeSum/Scales.lean at commit
2b639655e07421b9ac743de9090459bab473a7c0 (Apache-2.0).
These definitions describe the changed schedule; their integration into
the complete Light/word-RAM solver is a separate obligation.
-/

namespace ThreeSum1960614.Schedule

def inputBits (n : ℕ) : ℕ := Nat.log2 n

def microSize (m : ℕ) : ℕ := 2 * (Nat.nthRoot 3 m / 2)

def blockCount (m : ℕ) : ℕ :=
  20 * (203889696 * m / (20000000000 * microSize m))

def totalSize (m : ℕ) : ℕ := blockCount m * microSize m

def bandExponent (m : ℕ) : ℕ := 62656016 * totalSize m / 1000000000

def bandDivisor (m : ℕ) : ℕ := 2 ^ bandExponent m

end ThreeSum1960614.Schedule
