import Submission.ThreeSum.Switch
import Submission.ThreeSum.ActualQuarticSwitch

/-! Compatibility interface consumed by the full reporting driver.
It delegates to the proved degree-four Light procedure. No cubic test or
separate callback implementation remains in this execution path. -/

namespace ThreeSum.LightSwitch
open Light
abbrev word := ThreeSum1960614.LightQuarticSwitch.word
abbrev test := ThreeSum1960614.LightQuarticSwitch.test
abbrev body := ThreeSum1960614.LightQuarticSwitch.body
def time (r : ℕ) : ℕ := ThreeSum1960614.LightQuarticSwitch.time r
def program : Program := [body]

theorem candidates_eq (J j r : ℕ) :
    Switch.candidates J j r = ThreeSum1960614.LightQuarticSwitch.candidates J j r := rfl

theorem index_eq (J j r : ℕ) :
    Switch.switchIndex J j r = ThreeSum1960614.LightQuarticSwitch.index J j r := rfl

theorem index_le_residual {J j r : ℕ} (hne : (Switch.candidates J j r).Nonempty) :
    Switch.switchIndex J j r ≤ r :=
  ThreeSum1960614.LightQuarticSwitch.index_le_residual hne

theorem actual_candidates_nonempty {n j : ℕ} (hj : j ≤ Switch.terminalDepth n) :
    (Switch.candidates (Scales.blockCount (Scales.inputBits n)) j
      (Switch.residualSize n j)).Nonempty := by
  exact ThreeSum1960614.LightQuarticSwitch.actual_candidates_nonempty hj

theorem meets {lim : Limits} {P : Program} {μ : ℕ→ℤ} {J j r d p : ℕ}
    (hp : P[p]?=some body) (hj : j ≤ J) (hne : (Switch.candidates J j r).Nonempty)
    (hword : (word J r : ℤ) ≤ lim.word) :
    Meets lim P p d [J,j,r] μ (time r)
      (fun result ν => result=(Switch.switchIndex J j r : ℤ) ∧ ν=μ) := by
  exact ThreeSum1960614.LightQuarticSwitch.meets hp hj hne hword

theorem program_meets {lim : Limits} {μ : ℕ→ℤ} {J j r d : ℕ}
    (hj : j ≤ J) (hne : (Switch.candidates J j r).Nonempty)
    (hword : (word J r : ℤ) ≤ lim.word) :
    Meets lim program 0 d [J,j,r] μ (time r)
      (fun result ν => result=(Switch.switchIndex J j r : ℤ) ∧ ν=μ) :=
  meets rfl hj hne hword

theorem actual_meets {lim : Limits} {μ : ℕ→ℤ} {n j d : ℕ}
    (hj : j ≤ Switch.terminalDepth n)
    (hword : (word (Scales.blockCount (Scales.inputBits n))
      (Switch.residualSize n j) : ℤ) ≤ lim.word) :
    Meets lim program 0 d [Scales.blockCount (Scales.inputBits n),j,Switch.residualSize n j] μ
      (time (Switch.residualSize n j))
      (fun result ν => result=(Switch.actualSwitch n j : ℤ) ∧ ν=μ) := by
  exact ThreeSum1960614.LightQuarticSwitch.actual_meets hj hword

end ThreeSum.LightSwitch
