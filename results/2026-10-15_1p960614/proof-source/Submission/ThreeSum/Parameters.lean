import Submission.Closed3Sum.encoding_parameter_bounds
import Submission.Closed3Sum.quartic_parameter_certificate
import Submission.Closed3Sum.quartic_switch_bounds
import Submission.Closed3Sum.uniform_entropy_bound
import Mathlib.Analysis.Complex.ExponentialBounds

/-!
Expansion-232 analytic interface for the actual machine-source modules.
The definition bodies use the audited rational quartic parameter choice.
Closed analytic proofs supply the bounds; no program correctness contract
is assumed by this interface. Additional operational exponents must remain
the individual raw ledger costs for the universal rational-r bridge.
-/

noncomputable section
namespace ThreeSum.Parameters
open Set

def entropy (t : ℝ) : ℝ := Real.binEntropy t / Real.log 2
def E : ℝ := 116 * entropy (1 / 232)
def kappa : ℝ := 464 * entropy (1 / 464) - 232 * entropy (1 / 232) - 1
def gamma (t : ℝ) : ℝ := 232 * entropy (1 / 232) - 232 * entropy ((1-t)/232)
def phi (t : ℝ) : ℝ :=
  (785174904*t+72447023*t^2+24044466*t^3+12022459*t^4)/100000000
def phiDeriv (t : ℝ) : ℝ :=
  (785174904+2*72447023*t+3*24044466*t^2+4*12022459*t^3)/100000000
def epsilon : ℝ := 203889696/1000000000
def bandShift : ℝ := -(62656016/1000000000)
def boxSaving : ℝ := 193175570/1000000000
def initialTheta : ℝ := 40409899/1000000000
def terminalFraction : ℝ := 13/20
def entropyRatio : ℝ := 2790503/10000000
def tangentPoint : ℝ := 17200068185091493/100000000000000000
def kappaCap : ℝ := 1557987216579/1000000000000000
def certificateExponent : ℝ := 196061388/100000000
def targetExponent : ℝ := 980307/500000

theorem log_two_pos : 0 < Real.log 2 := Real.log_pos (by norm_num)
theorem log_two_lower : (2/3 : ℝ) < Real.log 2 := by linarith [Real.log_two_gt_d9]
theorem log_two_upper : Real.log 2 < (25/36 : ℝ) := by linarith [Real.log_two_lt_d9]

theorem E_bounds : (4 : ℝ) < E ∧ E < 19/4 := by
  obtain ⟨hl,hu,_,_⟩ := ThreeSum1960614.encoding_parameter_bounds
  have he : E = ThreeSum1960614.E 232 := by
    norm_num [E,entropy,ThreeSum1960614.E,ThreeSum1960614.entropy]
  rw [he]
  constructor <;> linarith

theorem epsilon_positive : 0 < epsilon := by norm_num [epsilon]
theorem epsilon_lt_one : epsilon < 1 := by norm_num [epsilon]
theorem kappa_positive : 0 < kappa := by
  obtain ⟨_,_,hl,_⟩ := ThreeSum1960614.encoding_parameter_bounds
  have hk : kappa = ThreeSum1960614.kappa 232 := by
    norm_num [kappa,entropy,ThreeSum1960614.kappa,ThreeSum1960614.entropy]
  rw [hk]
  linarith
theorem kappa_bound : kappa < kappaCap := by
  obtain ⟨_,_,_,hu⟩ := ThreeSum1960614.encoding_parameter_bounds
  have hk : kappa = ThreeSum1960614.kappa 232 := by
    norm_num [kappa,entropy,ThreeSum1960614.kappa,ThreeSum1960614.entropy]
  rw [hk,kappaCap]
  exact hu
theorem certificate_lt_target : certificateExponent < targetExponent := by
  norm_num [certificateExponent,targetExponent]

/-- Every operational charge is retained for the arbitrary-target runtime bridge. -/
def costLedger (e k h : ℝ) : List ℝ :=
  [2 * epsilon * e,
   1 + epsilon * (e - bandShift),
   2 - epsilon * boxSaving,
   2 - epsilon * (1 / 2 + bandShift - h),
   2 - epsilon * (1 / 2 - bandShift - k - entropyRatio * (1 + boxSaving - 2 * bandShift)),
   2 - epsilon * (terminalFraction - 1 / 2 - bandShift - k),
   epsilon * (8 / 5) * (e + 1 / 2),
   2 + epsilon * (4 / 5 - (2 / 5) * e - 2 * bandShift),
   1 + epsilon * (1 / 2 - bandShift),
   2 - epsilon * (e + bandShift),
   2 - 2 * epsilon * (e + bandShift),
   1]

theorem actual_costLedger_eq :
    costLedger E kappa (entropy initialTheta) = ThreeSum1960614.costs := by
  norm_num [costLedger,E,kappa,entropy,epsilon,bandShift,boxSaving,terminalFraction,
    entropyRatio,initialTheta,ThreeSum1960614.costs,ThreeSum1960614.ledger,
    ThreeSum1960614.E,ThreeSum1960614.kappa,ThreeSum1960614.entropy,
    ThreeSum1960614.epsilon,ThreeSum1960614.beta,ThreeSum1960614.saving,
    ThreeSum1960614.tau,ThreeSum1960614.rho,ThreeSum1960614.theta]

theorem all_costs_lt_certificate :
    ∀ t ∈ costLedger E kappa (entropy initialTheta), t < certificateExponent := by
  rw [actual_costLedger_eq]
  exact ThreeSum1960614.quartic_parameter_certificate.2.2.2.2.2.2.2.2.2.1

theorem all_costs_le_certificate :
    ∀ t ∈ costLedger E kappa (entropy initialTheta), t ≤ certificateExponent :=
  fun t ht => (all_costs_lt_certificate t ht).le

theorem all_costs_lt_target :
    ∀ t ∈ costLedger E kappa (entropy initialTheta), t < targetExponent :=
  fun t ht => lt_of_le_of_lt (all_costs_le_certificate t ht) certificate_lt_target

theorem finite_cost_upper_below (charges : List ℝ) {r : ℝ}
    (hr : ∀ t ∈ charges, t < r) :
    ∃ a : ℝ, a < r ∧ ∀ t ∈ charges, t ≤ a := by
  induction charges with
  | nil =>
      refine ⟨r-1,by linarith,?_⟩
      simp
  | cons x xs ih =>
      have hx : x < r := hr x (by simp)
      obtain ⟨a,ha,hu⟩ := ih (fun t ht => hr t (by simp [ht]))
      refine ⟨max ((x+r)/2) a,max_lt (by linarith) ha,?_⟩
      intro t ht
      rcases List.mem_cons.mp ht with rfl | ht
      · exact (by linarith : t ≤ (t+r)/2).trans (le_max_left _ _)
      · exact (hu t ht).trans (le_max_right _ _)

theorem phi_zero : phi 0=0 := by norm_num [phi]
theorem phi_half : phi (1/2)=(6631298715/1600000000 : ℝ) := by norm_num [phi]
theorem phi_initial : boxSaving-2*bandShift < phi initialTheta := by
  norm_num [boxSaving,bandShift,phi,initialTheta]

theorem phi_derivative_lt_nine {t : ℝ} (ht : t ∈ Icc (0 : ℝ) (1/2)) :
    phiDeriv t < 9 := by
  have h := (ThreeSum1960614.quartic_switch_bounds t ht).2.2.1
  simpa only [phiDeriv,ThreeSum1960614.phiDeriv] using h

theorem phi_le_gamma {t : ℝ} (ht : t ∈ Icc (0 : ℝ) (1/2)) : phi t ≤ gamma t := by
  have h := (ThreeSum1960614.quartic_switch_bounds t ht).1
  norm_num [phi,gamma,entropy,ThreeSum1960614.phi,ThreeSum1960614.gamma,
    ThreeSum1960614.entropy] at h ⊢
  exact h

theorem entropy_phi_bound {t : ℝ} (ht : t ∈ Icc (0 : ℝ) (1/2)) :
    entropy t < entropyRatio*(1+phi t) := by
  simpa only [entropy,entropyRatio,phi,ThreeSum1960614.entropy,
    ThreeSum1960614.rho,ThreeSum1960614.phi] using ThreeSum1960614.uniform_entropy_bound t ht

theorem hasDerivAt_phi (t : ℝ) : HasDerivAt phi (phiDeriv t) t := by
  have hd := (((((hasDerivAt_id t).const_mul 785174904).add
    (((hasDerivAt_id t).pow 2).const_mul 72447023)).add
      (((hasDerivAt_id t).pow 3).const_mul 24044466)).add
        (((hasDerivAt_id t).pow 4).const_mul 12022459)).div_const 100000000
  change HasDerivAt phi _ t at hd
  apply hd.congr_deriv
  dsimp [phiDeriv]
  ring

theorem phi_increment_bound {u v : ℝ}
    (hu : u ∈ Icc (0 : ℝ) (1/2)) (hv : v ∈ Icc (0 : ℝ) (1/2)) (huv : u < v) :
    phi v-phi u < 9*(v-u) := by
  apply (convex_Icc (0 : ℝ) (1/2)).image_sub_lt_mul_sub_of_deriv_lt
    (fun y _ => (hasDerivAt_phi y).continuousAt.continuousWithinAt)
    (fun y _ => (hasDerivAt_phi y).differentiableAt.differentiableWithinAt)
    (fun y hy => ?_) u hu v hv huv
  rw [(hasDerivAt_phi y).deriv]
  exact phi_derivative_lt_nine (interior_subset hy)

theorem phi_step_rounding {u v m K : ℝ}
    (hu : u ∈ Icc (0 : ℝ) (1/2)) (hv : v ∈ Icc (0 : ℝ) (1/2))
    (hm : 0 < m) (hstep : v-u=1/m) (hprev : phi u < K) : phi v < K+9/m := by
  have huv : u < v := by
    have hpositive : 0 < 1/m := by positivity
    linarith
  have h := phi_increment_bound hu hv huv
  rw [hstep] at h
  rw [show 9/m=9*(1/m) by ring]
  linarith

def switchThreshold (a : ℝ) : ℝ := (boxSaving-2*bandShift+a)/(1-a)

theorem switchThreshold_upper {a : ℝ} (ha : a ∈ Icc (0 : ℝ) terminalFraction) :
    switchThreshold a ≤ 3 := by
  have hden : 0 < 1-a := by dsimp [terminalFraction] at ha; linarith [ha.2]
  rw [switchThreshold,div_le_iff₀ hden]
  dsimp [boxSaving,bandShift,terminalFraction] at *
  linarith [ha.2]

theorem switch_box_bound {a t : ℝ} (ha : a ∈ Icc (0 : ℝ) terminalFraction)
    (ht : t ∈ Icc (0 : ℝ) (1/2)) (hswitch : switchThreshold a ≤ phi t) :
    boxSaving ≤ 2*bandShift-a+(1-a)*gamma t := by
  have hden : 0 < 1-a := by dsimp [terminalFraction] at ha; linarith [ha.2]
  have hs := (div_le_iff₀ hden).mp hswitch
  have hg := mul_le_mul_of_nonneg_left (phi_le_gamma ht) hden.le
  linarith

theorem switch_entropy_bound {a t mu : ℝ}
    (ha : a ∈ Icc (0 : ℝ) terminalFraction) (ht : t ∈ Icc (0 : ℝ) (1/2))
    (hmu : 0 < mu) (hswitch : phi t < switchThreshold a+9/((1-a)*mu)) :
    (1-a)*entropy t < entropyRatio*(1+boxSaving-2*bandShift)+9*entropyRatio/mu := by
  have hden : 0 < 1-a := by dsimp [terminalFraction] at ha; linarith [ha.2]
  have hr : 0 < entropyRatio := by norm_num [entropyRatio]
  have hh := mul_lt_mul_of_pos_left (entropy_phi_bound ht) hden
  have hp := mul_lt_mul_of_pos_left hswitch (mul_pos hden hr)
  have hid : (1-a)*entropyRatio*(1+(switchThreshold a+9/((1-a)*mu))) =
      entropyRatio*(1+boxSaving-2*bandShift)+9*entropyRatio/mu := by
    unfold switchThreshold
    field_simp [ne_of_gt hden,ne_of_gt hmu]
    ring
  rw [← hid]
  nlinarith

end ThreeSum.Parameters
