import Mathlib

/-
Copyright (c) 2026 Alexander Richard Towell. Released under the MIT license.
Formalized with substantial OpenAI Codex assistance from the written
Towell/Claude dyadic proof; Pico independently checked finite instances.
-/

namespace Family132

/-- Python's `bit_length(x XOR y)`, including label zero on the diagonal. -/
def label (x y : ℕ) : ℕ := Nat.size (x ^^^ y)

/-- Only the induced orientation on the chosen set is relevant. -/
def TournamentOn (S : Finset ℕ) (R : ℕ → ℕ → Prop) : Prop :=
  (∀ x ∈ S, ¬ R x x) ∧
  (∀ x ∈ S, ∀ y ∈ S, x ≠ y → R x y ∨ R y x) ∧
  (∀ x ∈ S, ∀ y ∈ S, R x y → ¬ R y x)

/-- Every vertex has a single label on all of its incoming edges in S.
Vertices with no incoming edges impose no condition. -/
def Bad (S : Finset ℕ) (R : ℕ → ℕ → Prop) : Prop :=
  ∀ x ∈ S, ∀ y ∈ S, ∀ z ∈ S, R x z → R y z → label x z = label y z

theorem label_self (x : ℕ) : label x x = 0 := by simp [label]

theorem label_comm (x y : ℕ) : label x y = label y x := by
  simp [label, Nat.xor_comm]

theorem label_le_of_same_bit {x y h : ℕ} (bound : label x y ≤ h + 1)
    (same : x.testBit h = y.testBit h) : label x y ≤ h := by
  apply Nat.size_le.mpr
  by_contra hn
  have ht := Nat.testBit_of_two_pow_le_and_two_pow_add_one_gt
    (Nat.le_of_not_gt hn) (Nat.size_le.mp bound)
  simp [Nat.testBit_xor, same] at ht

theorem label_eq_of_different_bit {x y h : ℕ} (bound : label x y ≤ h + 1)
    (diff : x.testBit h ≠ y.testBit h) : label x y = h + 1 := by
  have ht : (x ^^^ y).testBit h = true := by
    simp only [Nat.testBit_xor]
    cases hx : x.testBit h <;> cases hy : y.testBit h <;> simp_all
  have hl : h < label x y := Nat.lt_size.mpr (Nat.ge_two_pow_of_testBit ht)
  omega

theorem tournament_mono {S T : Finset ℕ} {R : ℕ → ℕ → Prop}
    (h : TournamentOn S R) (sub : T ⊆ S) : TournamentOn T R := by
  exact ⟨fun x hx => h.1 x (sub hx),
    fun x hx y hy hxy => h.2.1 x (sub hx) y (sub hy) hxy,
    fun x hx y hy hxy => h.2.2 x (sub hx) y (sub hy) hxy⟩

theorem bad_mono {S T : Finset ℕ} {R : ℕ → ℕ → Prop}
    (h : Bad S R) (sub : T ⊆ S) : Bad T R := by
  exact fun x hx y hy z hz => h x (sub hx) y (sub hy) z (sub hz)

theorem exists_internal_edge {S : Finset ℕ} {R : ℕ → ℕ → Prop}
    (t : TournamentOn S R) (hc : 1 < S.card) :
    ∃ x ∈ S, ∃ y ∈ S, R x y := by
  obtain ⟨x, hx, y, hy, hxy⟩ := Finset.one_lt_card.mp hc
  rcases t.2.1 x hx y hy hxy with he | he
  · exact ⟨x, hx, y, hy, he⟩
  · exact ⟨y, hy, x, hx, he⟩

/-- Two separated label clusters cannot both contain an internal edge. -/
theorem one_part_small {S A B : Finset ℕ} {R : ℕ → ℕ → Prop} {h : ℕ}
    (t : TournamentOn S R) (bad : Bad S R)
    (ha : A ⊆ S) (hb : B ⊆ S) (disj : Disjoint A B)
    (la : ∀ x ∈ A, ∀ y ∈ A, label x y ≤ h)
    (lb : ∀ x ∈ B, ∀ y ∈ B, label x y ≤ h)
    (cross : ∀ x ∈ A, ∀ y ∈ B, label x y = h + 1) :
    A.card ≤ 1 ∨ B.card ≤ 1 := by
  by_contra hn
  push Not at hn
  obtain ⟨a, haA, u, huA, hau⟩ := exists_internal_edge (tournament_mono t ha) hn.1
  obtain ⟨b, hbB, v, hvB, hbv⟩ := exists_internal_edge (tournament_mono t hb) hn.2
  have huv : u ≠ v := by
    intro he
    exact Finset.disjoint_left.mp disj huA (he ▸ hvB)
  rcases t.2.1 u (ha huA) v (hb hvB) huv with huv | hvu
  · have eq := bad b (hb hbB) u (ha huA) v (hb hvB) hbv huv
    have small := lb b hbB v hvB
    rw [cross u huA v hvB] at eq
    omega
  · have eq := bad a (ha haA) v (hb hvB) u (ha huA) hau hvu
    have small := la a haA u huA
    rw [label_comm v u, cross u huA v hvB] at eq
    omega

/-- The arbitrary-size dyadic bad-set bound. The pairwise formulation also
covers sets inside a translated binary prefix block. -/
theorem bad_card_le {h : ℕ} {S : Finset ℕ} {R : ℕ → ℕ → Prop}
    (t : TournamentOn S R) (bad : Bad S R)
    (bound : ∀ x ∈ S, ∀ y ∈ S, label x y ≤ h) : S.card ≤ h + 1 := by
  classical
  induction h generalizing S with
  | zero =>
    apply Finset.card_le_one.mpr
    intro x hx y hy
    have hz : x ^^^ y = 0 := Nat.size_eq_zero.mp (Nat.eq_zero_of_le_zero (bound x hx y hy))
    have he := congrArg (fun z => x ^^^ z) hz
    simpa [← Nat.xor_assoc] using he.symm
  | succ h ih =>
    let A := S.filter (fun x => x.testBit h = true)
    let B := S.filter (fun x => ¬ x.testBit h = true)
    have ha : A ⊆ S := Finset.filter_subset _ _
    have hb : B ⊆ S := Finset.filter_subset _ _
    have la : ∀ x ∈ A, ∀ y ∈ A, label x y ≤ h := by
      intro x hx y hy
      exact label_le_of_same_bit (bound x (ha hx) y (ha hy))
        ((Finset.mem_filter.mp hx).2.trans (Finset.mem_filter.mp hy).2.symm)
    have lb : ∀ x ∈ B, ∀ y ∈ B, label x y ≤ h := by
      intro x hx y hy
      apply label_le_of_same_bit (bound x (hb hx) y (hb hy))
      have hx' := (Finset.mem_filter.mp hx).2
      have hy' := (Finset.mem_filter.mp hy).2
      cases ex : x.testBit h <;> cases ey : y.testBit h <;> simp_all
    have cross : ∀ x ∈ A, ∀ y ∈ B, label x y = h + 1 := by
      intro x hx y hy
      apply label_eq_of_different_bit (bound x (ha hx) y (hb hy))
      have hx' := (Finset.mem_filter.mp hx).2
      have hy' := (Finset.mem_filter.mp hy).2
      intro eq
      exact hy' (eq ▸ hx')
    have disj : Disjoint A B := by
      apply Finset.disjoint_left.mpr
      intro x hx hy
      exact (Finset.mem_filter.mp hy).2 (Finset.mem_filter.mp hx).2
    have ac := ih (tournament_mono t ha) (bad_mono bad ha) la
    have bc := ih (tournament_mono t hb) (bad_mono bad hb) lb
    have sum : A.card + B.card = S.card := Finset.card_filter_add_card_filter_not _
    rcases one_part_small t bad ha hb disj la lb cross with small | small <;> omega

/-- Concrete form of Lemma A: any bad set of h-bit natural-number vertices
has at most h+1 elements, independently of the tournament orientation. -/
theorem bad_card_le_of_lt_two_pow {h : ℕ} {S : Finset ℕ} {R : ℕ → ℕ → Prop}
    (t : TournamentOn S R) (bad : Bad S R)
    (vertices : ∀ x ∈ S, x < 2 ^ h) : S.card ≤ h + 1 := by
  exact bad_card_le t bad (fun x hx y hy =>
    Nat.size_le.mpr (Nat.xor_lt_two_pow (vertices x hx) (vertices y hy)))

/-- Equivalence to unrestricted incoming-label choices. To require m_j in a
palette [r], additionally require r>0 and that all edge labels lie in [r].
Vertices with indegree zero impose no condition in `Bad`. -/
theorem bad_iff_incoming_label {S : Finset ℕ} {R : ℕ → ℕ → Prop} :
    Bad S R ↔ ∀ z ∈ S, ∃ m : ℕ, ∀ x ∈ S, R x z → label x z = m := by
  classical
  constructor
  · intro hb z hz
    by_cases hi : ∃ x ∈ S, R x z
    · obtain ⟨x, hx, hxz⟩ := hi
      exact ⟨label x z, fun y hy hyz => hb y hy x hx z hz hyz hxz⟩
    · exact ⟨0, fun x hx hxz => False.elim (hi ⟨x, hx, hxz⟩)⟩
  · intro hm x hx y hy z hz hxz hyz
    obtain ⟨m, he⟩ := hm z hz
    exact (he x hx hxz).trans (he y hy hyz).symm

/-- For k vertices indexed 0,...,k-1, `size (k-1)` is the exact integer
ceiling of log₂ k when k>0; the k=0 case is covered as well. -/
theorem bad_card_le_on_range {k : ℕ} {S : Finset ℕ} {R : ℕ → ℕ → Prop}
    (t : TournamentOn S R) (bad : Bad S R)
    (vertices : ∀ x ∈ S, x < k) : S.card ≤ Nat.size (k - 1) + 1 := by
  apply bad_card_le_of_lt_two_pow t bad
  intro x hx
  have hk := vertices x hx
  exact lt_of_le_of_lt (by omega : x ≤ k - 1) (Nat.lt_size_self (k - 1))


/-- The source's one-based vertices and explicit incoming-label witnesses.
No shift of the actual XOR formula is left to an informal identification. -/
theorem source_bad_card_le {k : ℕ} {S : Finset ℕ} {R : ℕ → ℕ → Prop}
    (t : TournamentOn S R)
    (vertices : ∀ i ∈ S, 1 ≤ i ∧ i ≤ k)
    (bad : ∀ j ∈ S, ∃ m : ℕ, ∀ i ∈ S, R i j → label (i - 1) (j - 1) = m) :
    S.card ≤ Nat.size (k - 1) + 1 := by
  classical
  let T := S.image (fun i => i - 1)
  let R' := fun x y => R (x + 1) (y + 1)
  have restore : ∀ i ∈ S, i - 1 + 1 = i := fun i hi =>
    Nat.sub_add_cancel (vertices i hi).1
  have tt : TournamentOn T R' := by
    refine ⟨?_, ?_, ?_⟩
    · intro x hx
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
      simpa only [R', restore i hi] using t.1 i hi
    · intro x hx y hy hxy
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
      obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hy
      have hij : i ≠ j := fun he => hxy (congrArg (fun n => n - 1) he)
      simpa only [R', restore i hi, restore j hj] using t.2.1 i hi j hj hij
    · intro x hx y hy
      obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
      obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hy
      simpa only [R', restore i hi, restore j hj] using t.2.2 i hi j hj
  have bt : Bad T R' := by
    apply bad_iff_incoming_label.mpr
    intro y hy
    obtain ⟨j, hj, rfl⟩ := Finset.mem_image.mp hy
    obtain ⟨m, hm⟩ := bad j hj
    refine ⟨m, ?_⟩
    intro x hx hxy
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
    apply hm i hi
    simpa only [R', restore i hi, restore j hj] using hxy
  have vt : ∀ x ∈ T, x < k := by
    intro x hx
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
    have hv := vertices i hi
    omega
  have ct : T.card = S.card := Finset.card_image_of_injOn (by
    intro i hi j hj he
    have hi' := vertices i hi
    have hj' := vertices j hj
    change i - 1 = j - 1 at he
    omega)
  rw [← ct]
  exact bad_card_le_on_range tt bt vt


end Family132
