import Submission.ThreeSum.FinalSolver
import Submission.ThreeSum.RawCostExponent

set_option autoImplicit false
set_option relaxedAutoImplicit false

namespace ThreeSum1960614

/-- The unchanged exact word-RAM goal for every strict rational ledger bound. -/
theorem costs_solve_3sum (r : ℚ) (hr : 0 < r)
    (hcost : ∀ z ∈ costs, z < (r : ℝ)) : EndStatement.ThreeSum.SolvedInTime r := by
  have hpos : (0 : ℝ) < (r : ℝ) := by exact_mod_cast hr
  have hgap : ThreeSum.Parameters.rawCostExponent < (r : ℝ) :=
    ThreeSum.Parameters.raw_exponent_lt_of_costs_lt hpos
      (by simpa only [ThreeSum.Parameters.actual_costLedger_eq] using hcost)
  apply ThreeSum.ThreeSumHybridEndBridge.endStatement_of_solvers_at hr hgap
  intro κ
  exact ⟨ThreeSum.ThreeSumWantedHostConditions.cutoff κ,
    ThreeSum.LightThreeSumHybrid.program κ,542,ThreeSum.LightThreeSumHybrid.need κ,
    ThreeSum.LightThreeSumHybrid.solves κ,ThreeSum.LightThreeSumHybrid.poly_need κ⟩

end ThreeSum1960614
