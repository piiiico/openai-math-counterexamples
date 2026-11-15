import Proof

namespace Family132.Controls

-- The exact intended statement, with no regularity/outdegree hypothesis.
example (h : ℕ) (S : Finset ℕ) (R : ℕ → ℕ → Prop)
    (ht : TournamentOn S R) (hb : Bad S R)
    (hv : ∀ x ∈ S, x < 2 ^ h) : S.card ≤ h + 1 :=
  bad_card_le_of_lt_two_pow ht hb hv

-- Nonvacuity and attainment: h=3, four vertices, transitive orientation.
theorem witness_tournament : TournamentOn {0, 1, 3, 7} (· < ·) := by
  unfold TournamentOn
  decide

theorem witness_bad : Bad {0, 1, 3, 7} (· < ·) := by
  unfold Bad label
  decide

theorem witness_bound : ∀ x ∈ ({0, 1, 3, 7} : Finset ℕ), x < 2 ^ 3 := by decide

theorem stronger_bound_false : ¬ ({0, 1, 3, 7} : Finset ℕ).card ≤ 3 := by decide

-- Empty and zero-bit cases.
example : TournamentOn ∅ (· < ·) := by simp [TournamentOn]
example : Bad ∅ (· < ·) := by simp [Bad]
example : TournamentOn {0} (· < ·) := by unfold TournamentOn; decide
example : Bad {0} (· < ·) := by unfold Bad label; decide
example : ({0} : Finset ℕ).card ≤ 0 + 1 := by decide

-- Without completeness of the orientation the bound is false.
theorem empty_relation_bad : Bad {0, 1, 2, 3} (fun _ _ => False) := by
  simp [Bad]
theorem missing_completeness : ¬ TournamentOn {0, 1, 2, 3} (fun _ _ => False) := by
  unfold TournamentOn
  decide
theorem empty_relation_exceeds : ¬ ({0, 1, 2, 3} : Finset ℕ).card ≤ 2 + 1 := by decide

-- A genuine tournament may fail the bad-set condition.
theorem nonbad_tournament : ¬ Bad {0, 1, 2, 3} (· < ·) := by
  unfold Bad label
  decide

end Family132.Controls
