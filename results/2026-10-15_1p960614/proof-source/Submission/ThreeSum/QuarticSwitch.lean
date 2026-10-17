import Submission.ThreeSum.LightSwitchScalar
import Submission.ThreeSum.ScaleDefinitions

/-!
The actual quartic integer test and its Light-language execution contract.
The finite scan and proof structure adapt the pinned Apache-2.0 source
Submission/ThreeSum/LightSwitch{,Bounds}.lean, commit
2b639655e07421b9ac743de9090459bab473a7c0.
The coefficients, powers and resource allowances below are changed to
the exact expansion-232 degree-four comparison in PROOF.md, Section 4.2.
-/

namespace ThreeSum1960614.LightQuarticSwitch

open Light
set_option maxHeartbeats 5000000
set_option maxRecDepth 12000

def polynomial (r q : ℕ) : ℕ :=
  q * (785174904*r*r*r + q*(72447023*r*r + q*(24044466*r + 12022459*q)))

def left (J j r : ℕ) : ℕ :=
  100000000*(159243801*J+500000000*j)*r*r*r*r

def factor (J j : ℕ) : ℕ := 500000000*(J-j)

def accepts (J j r q : ℕ) : Prop := left J j r ≤ factor J j * polynomial r q

instance (J j r q : ℕ) : Decidable (accepts J j r q) :=
  inferInstanceAs (Decidable (_ ≤ _))

def candidates (J j r : ℕ) : Finset ℕ :=
  (Finset.range (r/2+1)).filter (accepts J j r)

def index (J j r : ℕ) : ℕ :=
  if h : (candidates J j r).Nonempty then (candidates J j r).min' h else 0

def word (J r : ℕ) : ℕ := (J+r+1000000001)^96

@[simp] theorem mem_candidates {J j r q : ℕ} :
    q ∈ candidates J j r ↔ q ≤ r/2 ∧ accepts J j r q := by
  simp [candidates, Nat.lt_succ_iff]

theorem index_mem {J j r : ℕ} (h : (candidates J j r).Nonempty) :
    index J j r ∈ candidates J j r := by
  simp only [index, dif_pos h]
  exact Finset.min'_mem _ _

theorem index_le {J j r q : ℕ} (hq : q ∈ candidates J j r) : index J j r ≤ q := by
  have h : (candidates J j r).Nonempty := ⟨q,hq⟩
  simp only [index, dif_pos h]
  exact Finset.min'_le _ _ hq

theorem before_rejects {J j r q : ℕ}
    (hne : (candidates J j r).Nonempty) (hq : q < index J j r) :
    factor J j*polynomial r q < left J j r := by
  have hb := (mem_candidates.mp (index_mem hne)).1
  have hno : ¬ accepts J j r q := by
    intro h
    have hm := index_le (mem_candidates.mpr ⟨by omega,h⟩)
    omega
  unfold accepts at hno
  omega

theorem at_accepts {J j r : ℕ} (hne : (candidates J j r).Nonempty) :
    left J j r ≤ factor J j*polynomial r (index J j r) :=
  (mem_candidates.mp (index_mem hne)).2

theorem index_le_residual {J j r : ℕ} (hne : (candidates J j r).Nonempty) :
    index J j r ≤ r :=
  (mem_candidates.mp (index_mem hne)).1.trans (Nat.div_le_self _ _)

theorem accepts_cleared (J s j q : ℕ) :
    accepts J j ((J-j)*s) q ↔ clearedSwitch J s j q := by
  unfold accepts left factor polynomial clearedSwitch
  dsimp
  ring_nf

def test : Cond :=
  (k 500000000 *' (Light.v 0 -' Light.v 1) *'
    (Light.v 3 *' (k 785174904 *' Light.v 2 *' Light.v 2 *' Light.v 2 +'
      Light.v 3 *' (k 72447023 *' Light.v 2 *' Light.v 2 +'
        Light.v 3 *' (k 24044466 *' Light.v 2 +' k 12022459 *' Light.v 3))))) <'
    (k 100000000 *' (k 159243801 *' Light.v 0 +' k 500000000 *' Light.v 1) *'
      Light.v 2 *' Light.v 2 *' Light.v 2 *' Light.v 2)

def body : Stmt :=
  .set 3 (k 0) ;;
  .while test (.set 3 (Light.v 3 +' k 1)) ;;
  .set 0 (Light.v 3)

def time (r : ℕ) : ℕ := 200*(r+1)+100

variable {lim : Limits} {P : Program} {μ : ℕ→ℤ} {J j r q d : ℕ}

theorem frame_vars_bound (hj : j ≤ J) (hq : q ≤ r) :
    ∀ i, |(frame [(J : ℤ),j,r,q]) i| ≤ ((J+r+1000000001 : ℕ) : ℤ) := by
  intro i
  rcases i with _ | _ | _ | _ | i <;> simp [frame] <;> omega

theorem test_safe (hj : j ≤ J) (hq : q ≤ r)
    (hword : (word J r : ℤ) ≤ lim.word) :
    test.Safe lim ⟨frame [(J : ℤ),j,r,q],μ⟩ := by
  have hv := frame_vars_bound hj hq
  have hB : 2 ≤ J+r+1000000001 := by omega
  unfold test Cond.Safe
  constructor
  · apply ThreeSum.LightSwitchScalar.scalar_safe hB _ hv
      _ (by
        simp only [ThreeSum.LightSwitchScalar.Small, and_true, true_and, and_assoc]
        exact ⟨by omega, by omega, by omega, by omega, by omega⟩)
    exact (Int.ofNat_le.mpr (Nat.pow_le_pow_right (by omega)
      (by decide : (k 500000000 *' (Light.v 0 -' Light.v 1) *'
        (Light.v 3 *' (k 785174904 *' Light.v 2 *' Light.v 2 *' Light.v 2 +'
          Light.v 3 *' (k 72447023 *' Light.v 2 *' Light.v 2 +'
            Light.v 3 *' (k 24044466 *' Light.v 2 +' k 12022459 *' Light.v 3))))).cost ≤ 96))).trans hword
  · apply ThreeSum.LightSwitchScalar.scalar_safe hB _ hv
      _ (by
        simp only [ThreeSum.LightSwitchScalar.Small, and_true, true_and, and_assoc]
        exact ⟨by omega, by omega, by omega⟩)
    exact (Int.ofNat_le.mpr (Nat.pow_le_pow_right (by omega)
      (by decide : (k 100000000 *' (k 159243801 *' Light.v 0 +' k 500000000 *' Light.v 1) *'
        Light.v 2 *' Light.v 2 *' Light.v 2 *' Light.v 2).cost ≤ 96))).trans hword

theorem test_holds_iff (hj : j ≤ J) :
    test.Holds ⟨frame [(J : ℤ),j,r,q],μ⟩ ↔ factor J j*polynomial r q < left J j r := by
  simp only [test,Cond.Holds,Expr.val,Op.eval,frame,List.getD_cons_zero,
    List.getD_cons_succ,Nat.cast_add,Nat.cast_ofNat]
  unfold factor polynomial left
  exact_mod_cast (Iff.rfl :
    500000000*(J-j)*(q*(785174904*r*r*r+q*(72447023*r*r+q*(24044466*r+12022459*q)))) <
      100000000*(159243801*J+500000000*j)*r*r*r*r ↔
    500000000*(J-j)*(q*(785174904*r*r*r+q*(72447023*r*r+q*(24044466*r+12022459*q)))) <
      100000000*(159243801*J+500000000*j)*r*r*r*r)

theorem meets {p : ℕ} (hp : P[p]?=some body) (hj : j ≤ J)
    (hne : (candidates J j r).Nonempty)
    (hword : (word J r : ℤ) ≤ lim.word) :
    Meets lim P p d [J,j,r] μ (time r)
      (fun result ν => result=(index J j r : ℤ) ∧ ν=μ) := by
  have hindex := index_le_residual hne
  have hbase : J+r+1000000001 ≤ word J r :=
    Nat.le_self_pow (by decide : (96 : ℕ) ≠ 0) _
  have hlinear : ((J+r+1000000001 : ℕ) : ℤ) ≤ lim.word :=
    (Int.ofNat_le.mpr hbase).trans hword
  apply Meets.of_body hp
  unfold body time
  light_set (0 : ℕ)
  refine Ends.next (150*index J j r+100) (Ends.whileBlock
    (fun i σ => σ=⟨frame [(J : ℤ),j,r,i],μ⟩)
    (index J j r) (by simp) ?round ?done (by light_time [test]))
    (hT := by light_time [test])
  case round =>
    rintro i _ hi rfl
    have hle : i ≤ r := by omega
    refine ⟨test_safe hj hle hword,
      (test_holds_iff hj).mpr (before_rejects hne hi),by light_side,?_⟩
    simp [update_frame_setLocal]
  case done =>
    rintro _ rfl
    refine ⟨test_safe hj hindex hword,?_,?_⟩
    · rw [test_holds_iff hj]
      exact not_lt_of_ge (at_accepts hne)
    · light_set (index J j r)
      exact ⟨rfl,rfl⟩

def program : Program := [body]

theorem program_meets (hj : j ≤ J) (hne : (candidates J j r).Nonempty)
    (hword : (word J r : ℤ) ≤ lim.word) :
    Meets lim program 0 d [J,j,r] μ (time r)
      (fun result ν => result=(index J j r : ℤ) ∧ ν=μ) :=
  meets rfl hj hne hword

end ThreeSum1960614.LightQuarticSwitch
