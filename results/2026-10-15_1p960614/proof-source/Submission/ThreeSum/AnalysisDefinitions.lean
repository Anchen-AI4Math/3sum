import Mathlib.Analysis.SpecialFunctions.BinaryEntropy
import Mathlib.Analysis.SpecialFunctions.Log.Deriv
import Mathlib.Analysis.Convex.Deriv
import Mathlib.Analysis.Calculus.MeanValue
import Mathlib.Analysis.SpecialFunctions.Pow.NthRootLemmas
import Mathlib.Analysis.SpecificLimits.Basic
import Mathlib.Analysis.SpecificLimits.Normed
import Mathlib.Data.Nat.Choose.Sum
import Mathlib.Data.Nat.Choose.Bounds
import Mathlib.Data.Finset.Max
import Mathlib.Tactic

set_option autoImplicit false
set_option relaxedAutoImplicit false

noncomputable section

namespace ThreeSum1960614

noncomputable def entropy (t : ℝ) : ℝ := Real.binEntropy t / Real.log 2
noncomputable def E (c : ℕ) : ℝ := (c : ℝ) / 2 * entropy (1 / c)
noncomputable def kappa (c : ℕ) : ℝ :=
  2 * c * entropy (1 / (2 * c)) - c * entropy (1 / c) - 1
noncomputable def gamma (c : ℕ) (t : ℝ) : ℝ :=
  c * entropy (1 / c) - c * entropy ((1 - t) / c)
def phi (t : ℝ) : ℝ :=
  (785174904 * t + 72447023 * t ^ 2 + 24044466 * t ^ 3 + 12022459 * t ^ 4) / 100000000
def phiDeriv (t : ℝ) : ℝ :=
  (785174904 + 2 * 72447023 * t + 3 * 24044466 * t ^ 2 + 4 * 12022459 * t ^ 3) / 100000000
def epsilon : ℝ := 203889696 / 1000000000
def beta : ℝ := -(62656016 / 1000000000)
def saving : ℝ := 193175570 / 1000000000
def theta : ℝ := 40409899 / 1000000000
def tau : ℝ := 13 / 20
def rho : ℝ := 2790503 / 10000000
def tangentPoint : ℝ := 17200068185091493 / 100000000000000000
def principal : ℝ := 196061388 / 100000000
def target : ℚ := 1960614 / 1000000
def v : ℝ := saving - 2 * beta
def threshold (a : ℝ) : ℝ := (v + a) / (1 - a)
def ledger (e b S terminal ratio EE kk hh : ℝ) : List ℝ :=
  [2 * e * EE,
   1 + e * (EE - b),
   2 - e * S,
   2 - e * (1 / 2 + b - hh),
   2 - e * (1 / 2 - b - kk - ratio * (1 + S - 2 * b)),
   2 - e * (terminal - 1 / 2 - b - kk),
   e * (8 / 5) * (EE + 1 / 2),
   2 + e * (4 / 5 - (2 / 5) * EE - 2 * b),
   1 + e * (1 / 2 - b),
   2 - e * (EE + b),
   2 - 2 * e * (EE + b), 1]
noncomputable def costs : List ℝ :=
  ledger epsilon beta saving tau rho (E 232) (kappa 232) (entropy theta)
def clearedSwitch (J s j q : ℕ) : Prop :=
  let r := (J - j) * s
  500000000 * (J - j) *
    (785174904 * q * r ^ 3 + 72447023 * q ^ 2 * r ^ 2 +
     24044466 * q ^ 3 * r + 12022459 * q ^ 4) ≥
    100000000 * (159243801 * J + 500000000 * j) * r ^ 4
noncomputable def ModelFeasible (c : ℕ) (e b S th terminal ratio R : ℝ) : Prop :=
  0 < e ∧ e < 1 ∧ b < 0 ∧ 0 < S ∧
  0 ≤ th ∧ th ≤ 1 / 2 ∧ 0 ≤ terminal ∧ terminal < 1 ∧
  0 < ratio ∧ S - 2 * b ≤ gamma c th ∧
  (∀ t ∈ Set.Icc (0 : ℝ) (1 / 2), entropy t ≤ ratio * (1 + gamma c t)) ∧
  ∀ z ∈ ledger e b S terminal ratio (E c) (kappa c) (entropy th), z ≤ R

end ThreeSum1960614
