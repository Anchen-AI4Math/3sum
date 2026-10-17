import Submission.ThreeSum.RawCostExponent
import Submission.ThreeSum.ThreeSumHybridCosts
import Submission.ThreeSumApsp.RunningTimes.Sec3.Theorem22.ThreeSumLayout
import Submission.ThreeSumApsp.RunningTimes.FromClaims.Bounds
import Submission.ThreeSumApsp.Statements.Exponents

/-!
# Transfer the verified hybrid solver to the exact end-statement model

The premises below require an actual light-language solver of s3Task with
the frozen hybrid cost and a polynomial resource requirement. The existing
compiler realization supplies the word-RAM program. These interfaces do
not supply or assume away the executable solver obligation.
-/

namespace ThreeSum.ThreeSumHybridEndBridge

open Light

set_option maxHeartbeats 1200000
set_option maxRecDepth 12000

noncomputable section

theorem realized_of_solves {κ cutoff : ℕ} {P : Program} {p : ℕ}
    {need : ℕ→ℕ→Need}
    (hs : Solves s3Task P p (ThreeSumHybridCosts.time κ cutoff) need)
    (hp : PolyNeed need) :
    ThreeSumApsp.WordRam.Realized EndStatement.ThreeSum
      (timeUpTo (ThreeSumHybridCosts.time κ cutoff)) :=
  Light.Sec3.realized_threeSum _ (hs.solvedIn hp)

theorem solvedAt_of_solves {κ cutoff : ℕ} {P : Program} {p : ℕ}
    {need : ℕ→ℕ→Need}
    (hs : Solves s3Task P p (ThreeSumHybridCosts.time κ cutoff) need)
    (hp : PolyNeed need) :
    ThreeSumApsp.WordRam.SolvedInTimeAt EndStatement.ThreeSum κ (980307/500000 : ℝ) 0 := by
  apply ThreeSumApsp.FromClaims.solvedAt_of_realized
    (timeUpTo (ThreeSumHybridCosts.time κ cutoff)) κ (realized_of_solves hs hp) (C := 1)
  simpa only [pow_zero,mul_one,one_mul,Parameters.targetExponent] using
    ThreeSumHybridCosts.timeUpTo_eventually_target κ cutoff

theorem solvedAt_of_solves_at {κ cutoff : ℕ} {P : Program} {p : ℕ}
    {need : ℕ→ℕ→Need} {r : ℝ}
    (hgap : Parameters.rawCostExponent < r)
    (hs : Solves s3Task P p (ThreeSumHybridCosts.time κ cutoff) need)
    (hp : PolyNeed need) :
    ThreeSumApsp.WordRam.SolvedInTimeAt EndStatement.ThreeSum κ r 0 := by
  apply ThreeSumApsp.FromClaims.solvedAt_of_realized
    (timeUpTo (ThreeSumHybridCosts.time κ cutoff)) κ (realized_of_solves hs hp) (C := 1)
  simpa only [pow_zero,mul_one,one_mul] using
    ThreeSumHybridCosts.timeUpTo_eventually_at κ cutoff hgap

theorem endStatement_of_solvers_at {r : ℚ} (hr : 0 < r)
    (hgap : Parameters.rawCostExponent < (r : ℝ))
    (h : ∀ κ : ℕ, ∃ (cutoff : ℕ) (P : Program) (p : ℕ) (need : ℕ→ℕ→Need),
      Solves s3Task P p (ThreeSumHybridCosts.time κ cutoff) need ∧ PolyNeed need) :
    EndStatement.ThreeSum.SolvedInTime r := by
  have hall : ThreeSumApsp.WordRam.SolvedInTime EndStatement.ThreeSum (r : ℝ) 0 := by
    intro κ
    obtain ⟨cutoff,P,p,need,hs,hp⟩ := h κ
    exact solvedAt_of_solves_at hgap hs hp
  exact hall.endStatement rfl hr.le

/-- A family of concrete solver contracts yields the core-Lean rational
end statement, including every fixed magnitude exponent κ=0,1,2,... . -/
theorem endStatement_of_solvers
    (h : ∀ κ : ℕ, ∃ (cutoff : ℕ) (P : Program) (p : ℕ) (need : ℕ→ℕ→Need),
      Solves s3Task P p (ThreeSumHybridCosts.time κ cutoff) need ∧ PolyNeed need) :
    EndStatement.ThreeSum.SolvedInTime (980307/500000 : Rat) := by
  have hall : ThreeSumApsp.WordRam.SolvedInTime EndStatement.ThreeSum (980307/500000 : ℝ) 0 := by
    intro κ
    obtain ⟨cutoff,P,p,need,hs,hp⟩ := h κ
    exact solvedAt_of_solves hs hp
  exact hall.endStatement (by norm_num) (by norm_num)

end
end ThreeSum.ThreeSumHybridEndBridge
