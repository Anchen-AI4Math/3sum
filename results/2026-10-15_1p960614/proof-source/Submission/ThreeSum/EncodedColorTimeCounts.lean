import Submission.ThreeSum.RawCostExponent
import Submission.ThreeSum.EncodedColorTimeScales
import Submission.ThreeSum.ThreeSumColorBudgets

/-! # Exact physical count scales for the selected-color preprocessing -/

namespace ThreeSum.EncodedColorTime

open Filter Real Scales BandScales Parameters StageBounds ArithmeticStageBounds
open EncodedColorResources CostLedger HierarchyScales

set_option maxHeartbeats 1600000
set_option maxRecDepth 12000

noncomputable section

theorem band_powerBound : PowerBound bandSize (epsilon*(E+bandShift)) :=
  PowerBound.of_rate MassScales.bandSize_log_rate_shift

theorem count_powerBound :
    PowerBound (fun n => ColorBandBounds.count n (bandSize n)) (2*(1-epsilon*(E+bandShift))) := by
  apply powerBound_mono BandPrimeCosts.owner_count_powerBound
  exact Eventually.of_forall fun n => by
    have hs := SourceBandCosts.size_le_bandCount (n := n) (le_refl n)
    have hh := Nat.mul_le_mul_left 3 (Nat.pow_le_pow_left hs 2)
    exact hh.trans (Nat.le_succ _)

theorem incidence_powerBound :
    PowerBound EncodedColorStageCosts.incidenceCap (2-epsilon*(E+bandShift)) := by
  have hh := band_powerBound.mul count_powerBound
  convert hh using 1 <;> (first | rfl | ring)

theorem keys_powerBound :
    PowerBound (fun n => LightGuardedWanted.totalKeys (half n) (blocks n)) (2*epsilon*E) := by
  have hh := (PowerBound.of_rate TrimScales.scheduleCount_log_rate).mul
    (PowerBound.of_rate typedOutputs_log_ratio_tendsto)
  have he : (0 : ℝ)+2*epsilon*E=2*epsilon*E := by unfold epsilon; ring
  rw [he] at hh
  simpa only [half,blocks,ThreeSumColorBudgets.total_keys_eq] using hh

theorem wanted_rows_le (n : ℕ) :
    3*EncodedColorStageCosts.incidenceCap n*LightGuardedWanted.totalKeys (half n) (blocks n)/radix n ≤
      UniformStageBounds.wantedBudget n := by
  have hs := SourceBandCosts.size_le_bandCount (n := n) (le_refl n)
  have hcap : EncodedColorStageCosts.incidenceCap n ≤ bandSize n*(3*bandCount n^2) :=
    Nat.mul_le_mul_left _ (Nat.mul_le_mul_left 3 (Nat.pow_le_pow_left hs 2))
  have hc := Nat.mul_le_mul_right (LightGuardedWanted.totalKeys (half n) (blocks n))
    (Nat.mul_le_mul_left 3 hcap)
  have he : 3*(bandSize n*(3*bandCount n^2))*LightGuardedWanted.totalKeys (half n) (blocks n)=
      MassScales.wantedNumerator n := by
    rw [show LightGuardedWanted.totalKeys (half n) (blocks n)=
      TrimScales.scheduleCount n*typedOutputs n from ThreeSumColorBudgets.total_keys_eq n]
    unfold MassScales.wantedNumerator
    ring
  rw [he] at hc
  exact Nat.div_le_div_right hc

theorem wanted_rows_powerBound :
    PowerBound (fun n =>
      3*EncodedColorStageCosts.incidenceCap n*LightGuardedWanted.totalKeys (half n) (blocks n)/radix n)
      (2-epsilon*(1/2+bandShift)) :=
  powerBound_mono UniformStageBounds.wantedBudget_powerBound (Eventually.of_forall wanted_rows_le)

theorem incidence_three_halves : PowerBound EncodedColorStageCosts.incidenceCap (3/2) :=
  incidence_powerBound.mono_exponent (by have h := E_bounds.1; unfold bandShift epsilon; linarith)

theorem count_one : PowerBound (fun n => ColorBandBounds.count n (bandSize n)) 1 :=
  count_powerBound.mono_exponent (by have h := E_bounds.1; unfold bandShift epsilon; linarith)

theorem keys_certificate :
    PowerBound (fun n => LightGuardedWanted.totalKeys (half n) (blocks n)) rawCostExponent :=
  keys_powerBound.mono_exponent (all_costs_le_raw_exponent _ (by simp [costLedger]))

theorem incidence_certificate : PowerBound EncodedColorStageCosts.incidenceCap rawCostExponent :=
  incidence_three_halves.mono_exponent (by linarith [raw_exponent_lower])

theorem radix_certificate : PowerBound radix rawCostExponent :=
  (PowerBound.of_rate radix_log_ratio_tendsto).mono_exponent (by
    have h := E_bounds.2
    unfold epsilon
    have hraw := raw_exponent_lower
    linarith)

theorem wanted_rows_certificate :
    PowerBound (fun n =>
      3*EncodedColorStageCosts.incidenceCap n*LightGuardedWanted.totalKeys (half n) (blocks n)/radix n)
      rawCostExponent :=
  wanted_rows_powerBound.mono_exponent (by
    have hraw := raw_exponent_lower
    norm_num [bandShift,epsilon]
    linarith)

end
end ThreeSum.EncodedColorTime
