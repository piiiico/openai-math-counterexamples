import Mathlib.Data.Rat.Defs
import Mathlib.Tactic

/-! Bounded maximum recurrences: finite windows propagate multiplicative periods.
Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
-/
namespace Family088

def step (weight M : ℕ → ℚ) (D n : ℕ) : ℚ :=
  ((List.range D).map fun j => weight (j + 1) * M (n - (j + 1))).foldr max 0

lemma fold_max_scale (xs : List ℚ) (k : ℚ) (hk : 0 ≤ k) :
    (xs.map (k * ·)).foldr max 0 = k * xs.foldr max 0 := by
  induction xs with
  | nil => simp
  | cons x xs ih =>
      simp only [List.map_cons, List.foldr_cons]
      rw [ih, mul_max_of_nonneg _ _ hk]

theorem window_periodicity (weight M : ℕ → ℚ) (B D P : ℕ) (k : ℚ)
    (hk : 0 ≤ k)
    (hrec : ∀ n, B + D ≤ n → M n = step weight M D n)
    (hwindow : ∀ n, B ≤ n → n < B + D → M (n + P) = k * M n) :
    ∀ n, B ≤ n → M (n + P) = k * M n := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
      intro hn
      by_cases hsmall : n < B + D
      · exact hwindow n hn hsmall
      · have hlarge : B + D ≤ n := by omega
        rw [hrec (n + P) (by omega), hrec n hlarge]
        unfold step
        have hmap :
            (List.range D).map (fun j => weight (j + 1) * M (n + P - (j + 1))) =
            ((List.range D).map (fun j => weight (j + 1) * M (n - (j + 1)))).map
              (k * ·) := by
          rw [List.map_map]
          apply List.map_congr_left
          intro j hj
          have hjD : j < D := List.mem_range.mp hj
          have hbase : B ≤ n - (j + 1) := by omega
          have hlt : n - (j + 1) < n := by omega
          have hsub : n + P - (j + 1) = (n - (j + 1)) + P := by omega
          dsimp only [Function.comp_apply]
          rw [hsub, ih (n - (j + 1)) hlt hbase]
          ring
        rw [hmap, fold_max_scale _ _ hk]

#print axioms window_periodicity
end Family088

namespace Family088

def boundedStep (weight M : ℕ → ℚ) (D n : ℕ) : ℚ :=
  ((List.range D).map fun j =>
    if j + 1 ≤ n then weight (j + 1) * M (n - (j + 1)) else 0).foldr max 0

lemma boundedStep_eq_step (weight M : ℕ → ℚ) (D n : ℕ) (hn : D ≤ n) :
    boundedStep weight M D n = step weight M D n := by
  unfold boundedStep step
  congr 1
  apply List.map_congr_left
  intro j hj
  have hjD : j < D := List.mem_range.mp hj
  simp only [if_pos (show j + 1 ≤ n by omega)]

/-- A table satisfying the finite recurrence is forced by the initial values. -/
theorem prefix_agreement (weight M V : ℕ → ℚ) (D N : ℕ)
    (hzero : M 0 = V 0) (hone : M 1 = V 1)
    (hrec : ∀ n, 2 ≤ n → M n = boundedStep weight M D n)
    (htable : ∀ n, 2 ≤ n → n ≤ N → V n = boundedStep weight V D n) :
    ∀ n, n ≤ N → M n = V n := by
  intro n
  induction n using Nat.strong_induction_on with
  | h n ih =>
      intro hn
      by_cases h0 : n = 0
      · simpa [h0] using hzero
      by_cases h1 : n = 1
      · simpa [h1] using hone
      have h2 : 2 ≤ n := by omega
      rw [hrec n h2, htable n h2 hn]
      unfold boundedStep
      congr 1
      apply List.map_congr_left
      intro j hj
      split_ifs with hjn
      · rw [ih (n - (j + 1)) (by omega) (by omega)]
      · rfl

end Family088
