import Submission.ThreeSum.QuarticSwitch
import Submission.Closed3Sum.integer_schedule

/-! Connect the proved finite schedule to the executed quartic scan.
The zero-residual branch is handled directly, so small inputs do not
silently require a positive microblock or a positive block count. -/

namespace ThreeSum1960614.LightQuarticSwitch

open Light Schedule
set_option maxHeartbeats 5000000

def residualSize (n j : ℕ) : ℕ := (blockCount (inputBits n)-j)*microSize (inputBits n)

def terminalDepth (n : ℕ) : ℕ := 13*blockCount (inputBits n)/20

def actualIndex (n j : ℕ) : ℕ :=
  index (blockCount (inputBits n)) j (residualSize n j)

theorem actual_depth_condition {n j : ℕ} (hj : j ≤ terminalDepth n) :
    20*j ≤ 13*blockCount (inputBits n) := by
  have h := Nat.div_mul_le_self (13*blockCount (inputBits n)) 20
  unfold terminalDepth at hj
  omega

theorem actual_candidates_nonempty {n j : ℕ} (hj : j ≤ terminalDepth n) :
    (candidates (blockCount (inputBits n)) j (residualSize n j)).Nonempty := by
  by_cases hz : residualSize n j=0
  · refine ⟨0,mem_candidates.mpr ⟨by omega,?_⟩⟩
    simp [accepts,left,polynomial,hz]
  · have hdepth := actual_depth_condition hj
    have hJ : 0 < blockCount (inputBits n) := by
      unfold residualSize at hz
      by_contra h
      have he : blockCount (inputBits n)=0 := by omega
      simp [he] at hz
    have hs : 0 < microSize (inputBits n) := by
      unfold residualSize at hz
      by_contra h
      have he : microSize (inputBits n)=0 := by omega
      simp [he] at hz
    have hlt : j < blockCount (inputBits n) := by omega
    have heven : Even (microSize (inputBits n)) := by
      unfold microSize
      exact even_two.mul_right _
    have hlevel : (j : ℝ)/blockCount (inputBits n) ≤ tau := by
      have hJR : (0 : ℝ) < blockCount (inputBits n) := by exact_mod_cast hJ
      rw [div_le_iff₀ hJR]
      have hd : (20 : ℝ)*j ≤ 13*blockCount (inputBits n) := by exact_mod_cast hdepth
      dsimp [tau]
      linarith
    obtain ⟨q,_,hbound,hclear,_⟩ :=
      ThreeSum1960614.integer_schedule (blockCount (inputBits n))
        (microSize (inputBits n)) j hJ hs heven hlt hlevel
    exact ⟨q,mem_candidates.mpr ⟨hbound,
      (accepts_cleared (blockCount (inputBits n)) (microSize (inputBits n)) j q).mpr hclear⟩⟩

theorem actual_meets {lim : Limits} {μ : ℕ→ℤ} {n j d : ℕ}
    (hj : j ≤ terminalDepth n)
    (hword : (word (blockCount (inputBits n)) (residualSize n j) : ℤ) ≤ lim.word) :
    Meets lim program 0 d
      [blockCount (inputBits n),j,residualSize n j] μ (time (residualSize n j))
      (fun result ν => result=(actualIndex n j : ℤ) ∧ ν=μ) := by
  have hdepth := actual_depth_condition hj
  exact program_meets (by omega) (actual_candidates_nonempty hj) hword

end ThreeSum1960614.LightQuarticSwitch
