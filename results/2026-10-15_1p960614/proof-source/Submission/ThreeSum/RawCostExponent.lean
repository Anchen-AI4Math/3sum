import Submission.ThreeSum.Parameters

/-!
The actual finite maximum of the twelve operational charges. Using this
exponent in the complete runtime assembly retains every strict target
above the maximum, including targets below the convenient principal cap.
-/

noncomputable section
namespace ThreeSum.Parameters

def rawCostExponent : ℝ :=
  (costLedger E kappa (entropy initialTheta)).foldr max 0

theorem fold_max_upper (charges : List ℝ) :
    ∀ t ∈ charges, t ≤ charges.foldr max 0 := by
  induction charges with
  | nil => simp
  | cons x xs ih =>
      intro t ht
      rcases List.mem_cons.mp ht with rfl | ht
      · exact le_max_left _ _
      · exact (ih t ht).trans (le_max_right _ _)

theorem fold_max_lt (charges : List ℝ) {r : ℝ} (hr : 0 < r)
    (hcharges : ∀ t ∈ charges, t < r) : charges.foldr max 0 < r := by
  induction charges with
  | nil => exact hr
  | cons x xs ih =>
      exact max_lt (hcharges x (by simp))
        (ih (fun t ht => hcharges t (by simp [ht])))

theorem all_costs_le_raw_exponent :
    ∀ t ∈ costLedger E kappa (entropy initialTheta), t ≤ rawCostExponent :=
  fold_max_upper _

theorem raw_exponent_lt_of_costs_lt {r : ℝ} (hr : 0 < r)
    (hcost : ∀ t ∈ costLedger E kappa (entropy initialTheta), t < r) :
    rawCostExponent < r := fold_max_lt _ hr hcost

theorem raw_exponent_lt_principal : rawCostExponent < certificateExponent :=
  fold_max_lt _ (by norm_num [certificateExponent]) all_costs_lt_certificate

theorem raw_exponent_lt_target : rawCostExponent < targetExponent :=
  raw_exponent_lt_principal.trans certificate_lt_target

theorem raw_exponent_lower : (193/100 : ℝ) ≤ rawCostExponent := by
  have hb : 2-epsilon*boxSaving ≤ rawCostExponent :=
    all_costs_le_raw_exponent _ (by simp [costLedger])
  exact (by norm_num [epsilon,boxSaving] : (193/100 : ℝ) ≤ 2-epsilon*boxSaving).trans hb

theorem raw_exponent_nonnegative : (0 : ℝ) ≤ rawCostExponent := by
  linarith [raw_exponent_lower]

end ThreeSum.Parameters
