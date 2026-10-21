/-
Modifications copyright (c) 2026 Alexander Richard Towell.
SPDX-License-Identifier: Apache-2.0
See ../source/LICENSE for the inherited OpenAI source license.
Substantial OpenAI Codex assistance.
The five source fields and cardinality arguments are adapted from
OpenAI math@1581d4cbdd69a0faf34b2089614fe2a814316a6a,
lean/OAI/Geometry/Borsuk/TenLabels/Labels.lean. Only `down` is omitted.
This module proves a translation, not certificate-checker soundness or geometry.
-/
import Mathlib

namespace Family156Bridge

abbrev Labels := Fin 10
abbrev Family := Finset Labels → Prop

section SourceDefinition
attribute [local instance] Classical.propDecidable

structure FiveFields (T Q : Family) : Prop where
  tetra_card : ∀ S, Q S → S.card = 4
  pure : ∀ U, T U → ∃ S, Q S ∧ U ⊆ S
  no_boundary : ∀ S U, Q S → U ⊆ S → U.card = 3 →
    ∃ S', Q S' ∧ U ⊆ S' ∧ S' ≠ S
  complementary : ∀ S U, Q S → U ⊆ Sᶜ → U.card = 3 →
    (T U ↔ ¬ T (Sᶜ \ U))
  pair_count : ∀ S P, Q S → P ⊆ Sᶜ → P.card = 2 →
    ((Sᶜ \ P).filter (fun w => T (insert w P))).card = 2

end SourceDefinition

def subsets (k : Nat) : List (Finset Labels) :=
  (((List.finRange 10).sublistsLen k).map List.toFinset).mergeSort
    (fun a b => !(b.sort (· ≤ ·)).lex (a.sort (· ≤ ·)) (fun i j => decide (i < j)))

@[simp] theorem mem_subsets {U : Finset Labels} {k : Nat} :
    U ∈ subsets k ↔ U.card = k := by
  simp only [subsets, List.mem_mergeSort, List.mem_map]
  constructor
  · rintro ⟨l, hl, rfl⟩
    obtain ⟨hsub, hlen⟩ := List.mem_sublistsLen.mp hl
    have hn : l.Nodup := (List.nodup_finRange 10).sublist hsub
    simpa [List.toFinset_card_of_nodup hn] using hlen
  · intro hc
    refine ⟨U.sort (· ≤ ·), ?_, Finset.sort_toFinset _ _⟩
    apply List.mem_sublistsLen.mpr
    refine ⟨?_, by simpa using hc⟩
    apply List.sublist_of_subperm_of_pairwise (r := fun (a b : Labels) => a ≤ b)
    · apply List.subperm_of_subset (Finset.sort_nodup U (· ≤ ·))
      intro x hx
      simp
    · exact Finset.pairwise_sort U (· ≤ ·)
    · exact List.pairwise_le_finRange 10


inductive Var where
  | triangle (U : Finset Labels)
  | tetra (S : Finset Labels)
  deriving DecidableEq

structure Literal where
  positive : Bool
  var : Var
  deriving DecidableEq

def SatLiteral (a : Var → Prop) (l : Literal) : Prop :=
  if l.positive then a l.var else ¬ a l.var
def SatClause (a : Var → Prop) (c : List Literal) : Prop :=
  ∃ l ∈ c, SatLiteral a l
def Satisfies (a : Var → Prop) (cnf : List (List Literal)) : Prop :=
  ∀ c ∈ cnf, SatClause a c
def model (T Q : Family) : Var → Prop
  | .triangle U => T U
  | .tetra S => Q S

def variableTable : List Var :=
  (subsets 3).map Var.triangle ++ (subsets 4).map Var.tetra
def GoodVar : Var → Prop
  | .triangle U => U.card = 3
  | .tetra S => S.card = 4

@[simp] theorem mem_variableTable {v : Var} : v ∈ variableTable ↔ GoodVar v := by
  cases v <;> simp [variableTable, GoodVar]

def varNumber (v : Var) : Nat := variableTable.idxOf v + 1

inductive Obligation where
  | pure (U : Finset Labels)
  | boundary (S U : Finset Labels)
  | complementPos (S U : Finset Labels)
  | complementNeg (S U : Finset Labels)
  | pairPos (S P R : Finset Labels)
  | pairNeg (S P R : Finset Labels)
  | nonempty
  deriving DecidableEq

def WellFormed : Obligation → Prop
  | .pure U => U.card = 3
  | .boundary S U => S.card = 4 ∧ U ⊆ S ∧ U.card = 3
  | .complementPos S U | .complementNeg S U =>
      S.card = 4 ∧ U ⊆ Sᶜ ∧ U.card = 3
  | .pairPos S P R | .pairNeg S P R =>
      S.card = 4 ∧ P ⊆ Sᶜ ∧ P.card = 2 ∧ R ⊆ Sᶜ \ P ∧ R.card = 3
  | .nonempty => True

instance (o : Obligation) : Decidable (WellFormed o) := by
  cases o <;> unfold WellFormed <;> infer_instance

def clause : Obligation → List Literal
  | .pure U => ⟨false, .triangle U⟩ ::
      ((subsets 4).filter (fun S => decide (U ⊆ S))).map (fun S => ⟨true, .tetra S⟩)
  | .boundary S U => ⟨false, .tetra S⟩ ::
      ((subsets 4).filter (fun V => decide (U ⊆ V ∧ V ≠ S))).map
        (fun V => ⟨true, .tetra V⟩)
  | .complementPos S U =>
      [⟨false, .tetra S⟩, ⟨true, .triangle U⟩, ⟨true, .triangle (Sᶜ \ U)⟩]
  | .complementNeg S U =>
      [⟨false, .tetra S⟩, ⟨false, .triangle U⟩, ⟨false, .triangle (Sᶜ \ U)⟩]
  | .pairPos S P R => ⟨false, .tetra S⟩ ::
      (R.sort (· ≤ ·)).map (fun w => ⟨true, .triangle (insert w P)⟩)
  | .pairNeg S P R => ⟨false, .tetra S⟩ ::
      (R.sort (· ≤ ·)).map (fun w => ⟨false, .triangle (insert w P)⟩)
  | .nonempty => (subsets 4).map (fun S => ⟨true, .tetra S⟩)

def rawObligations : List Obligation :=
  (subsets 3).flatMap (fun U => .pure U ::
    ((subsets 4).filter (fun S => decide (U ⊆ S))).map (fun S => .boundary S U)) ++
  (subsets 4).flatMap (fun S =>
    ((subsets 3).filter (fun U => decide (U ⊆ Sᶜ) &&
      decide (varNumber (.triangle U) < varNumber (.triangle (Sᶜ \ U))))).flatMap
        (fun U => [.complementPos S U, .complementNeg S U]) ++
    ((subsets 2).filter (fun P => decide (P ⊆ Sᶜ))).flatMap (fun P =>
      ((subsets 3).filter (fun R => decide (R ⊆ Sᶜ \ P))).flatMap
        (fun R => [.pairPos S P R, .pairNeg S P R]))) ++ [.nonempty]

-- Filtering makes the proof of schema well-formedness structural. Complete
-- exported-CNF equality is checked separately: omitted clauses cannot hide here.
def obligations := rawObligations.filter (fun o => decide (WellFormed o))
def generatedCNF := obligations.map clause

private theorem pair_pos {s r : Finset Labels} {p : Labels → Prop}
    [DecidablePred p] (hs : s.card = 4) (hr : r.card = 3) (hrs : r ⊆ s)
    (hp : (s.filter p).card = 2) : ∃ x ∈ r, p x := by
  by_contra hn
  have hsub : s.filter p ⊆ s \ r := by
    intro x hx
    obtain ⟨hxs, hpx⟩ := Finset.mem_filter.mp hx
    refine Finset.mem_sdiff.mpr ⟨hxs, ?_⟩
    intro hxr
    exact hn ⟨x, hxr, hpx⟩
  have hc := Finset.card_le_card hsub
  rw [Finset.card_sdiff_of_subset hrs, hs, hr, hp] at hc
  norm_num at hc

private theorem pair_neg {s r : Finset Labels} {p : Labels → Prop}
    [DecidablePred p] (hr : r.card = 3) (hrs : r ⊆ s)
    (hp : (s.filter p).card = 2) : ∃ x ∈ r, ¬ p x := by
  by_contra hn
  have hsub : r ⊆ s.filter p := by
    intro x hx
    apply Finset.mem_filter.mpr
    refine ⟨hrs hx, ?_⟩
    by_contra hnp
    exact hn ⟨x, hx, hnp⟩
  have hc := Finset.card_le_card hsub
  rw [hr, hp] at hc
  norm_num at hc

theorem source_satisfies_clause {T Q : Family} (h : FiveFields T Q)
    (hne : ∃ S, Q S) (o : Obligation) (hw : WellFormed o) :
    SatClause (model T Q) (clause o) := by
  classical
  cases o with
  | pure U =>
    by_cases hU : T U
    · obtain ⟨S, hS, hUS⟩ := h.pure U hU
      refine ⟨⟨true, .tetra S⟩, ?_, hS⟩
      simp [clause, h.tetra_card S hS, hUS]
    · exact ⟨⟨false, .triangle U⟩, by simp [clause], hU⟩
  | boundary S U =>
    by_cases hS : Q S
    · obtain ⟨V, hV, hUV, hVS⟩ := h.no_boundary S U hS hw.2.1 hw.2.2
      refine ⟨⟨true, .tetra V⟩, ?_, hV⟩
      simp [clause, h.tetra_card V hV, hUV, hVS]
    · exact ⟨⟨false, .tetra S⟩, by simp [clause], hS⟩
  | complementPos S U =>
    by_cases hS : Q S
    · have hc := h.complementary S U hS hw.2.1 hw.2.2
      simp only [SatClause, clause, List.mem_cons, List.not_mem_nil, or_false,
        exists_eq_or_imp, SatLiteral, Bool.false_eq_true, ↓reduceIte, model]
      tauto
    · exact ⟨⟨false, .tetra S⟩, by simp [clause], hS⟩
  | complementNeg S U =>
    by_cases hS : Q S
    · have hc := h.complementary S U hS hw.2.1 hw.2.2
      simp only [SatClause, clause, List.mem_cons, List.not_mem_nil, or_false,
        exists_eq_or_imp, SatLiteral, Bool.false_eq_true, ↓reduceIte, model]
      tauto
    · exact ⟨⟨false, .tetra S⟩, by simp [clause], hS⟩
  | pairPos S P R =>
    by_cases hS : Q S
    · have hc : (Sᶜ \ P).card = 4 := by
        rw [Finset.card_sdiff_of_subset hw.2.1, Finset.card_compl, hw.1, hw.2.2.1]
        decide
      obtain ⟨w, hwR, hTw⟩ := pair_pos hc hw.2.2.2.2 hw.2.2.2.1
        (h.pair_count S P hS hw.2.1 hw.2.2.1)
      exact ⟨⟨true, .triangle (insert w P)⟩, by simp only [clause, List.mem_cons, List.mem_map, Finset.mem_sort]; exact Or.inr ⟨w, hwR, rfl⟩, hTw⟩
    · exact ⟨⟨false, .tetra S⟩, by simp [clause], hS⟩
  | pairNeg S P R =>
    by_cases hS : Q S
    · obtain ⟨w, hwR, hTw⟩ := pair_neg hw.2.2.2.2 hw.2.2.2.1
        (h.pair_count S P hS hw.2.1 hw.2.2.1)
      exact ⟨⟨false, .triangle (insert w P)⟩, by simp only [clause, List.mem_cons, List.mem_map, Finset.mem_sort]; exact Or.inr ⟨w, hwR, rfl⟩, hTw⟩
    · exact ⟨⟨false, .tetra S⟩, by simp [clause], hS⟩
  | nonempty =>
    obtain ⟨S, hS⟩ := hne
    exact ⟨⟨true, .tetra S⟩, by simp [clause, h.tetra_card S hS], hS⟩

theorem model_satisfies_generated_cnf {T Q : Family} (h : FiveFields T Q)
    (hne : ∃ S, Q S) : Satisfies (model T Q) generatedCNF := by
  intro c hc
  obtain ⟨o, ho, rfl⟩ := List.mem_map.mp hc
  have hw : WellFormed o := by simpa [obligations] using (List.mem_filter.mp ho).2
  exact source_satisfies_clause h hne o hw

theorem clause_variables_good (o : Obligation) (hw : WellFormed o)
    (l : Literal) (hl : l ∈ clause o) : GoodVar l.var := by
  cases o with
  | pure U =>
    rcases List.mem_cons.mp hl with rfl | hl
    · exact hw
    · obtain ⟨S, hS, rfl⟩ := List.mem_map.mp hl
      exact mem_subsets.mp (List.mem_filter.mp hS).1
  | boundary S U =>
    rcases List.mem_cons.mp hl with rfl | hl
    · exact hw.1
    · obtain ⟨V, hV, rfl⟩ := List.mem_map.mp hl
      exact mem_subsets.mp (List.mem_filter.mp hV).1
  | complementPos S U =>
    simp only [clause, List.mem_cons, List.not_mem_nil, or_false] at hl
    rcases hl with rfl | rfl | rfl
    · exact hw.1
    · exact hw.2.2
    · change (Sᶜ \ U).card = 3
      rw [Finset.card_sdiff_of_subset hw.2.1, Finset.card_compl, hw.1, hw.2.2]
      decide
  | complementNeg S U =>
    simp only [clause, List.mem_cons, List.not_mem_nil, or_false] at hl
    rcases hl with rfl | rfl | rfl
    · exact hw.1
    · exact hw.2.2
    · change (Sᶜ \ U).card = 3
      rw [Finset.card_sdiff_of_subset hw.2.1, Finset.card_compl, hw.1, hw.2.2]
      decide
  | pairPos S P R =>
    rcases List.mem_cons.mp hl with rfl | hl
    · exact hw.1
    · obtain ⟨w, hwR, rfl⟩ := List.mem_map.mp hl
      have hwR' : w ∈ R := by simpa using hwR
      have hwP : w ∉ P := (Finset.mem_sdiff.mp (hw.2.2.2.1 hwR')).2
      change (insert w P).card = 3
      rw [Finset.card_insert_of_notMem hwP, hw.2.2.1]
  | pairNeg S P R =>
    rcases List.mem_cons.mp hl with rfl | hl
    · exact hw.1
    · obtain ⟨w, hwR, rfl⟩ := List.mem_map.mp hl
      have hwR' : w ∈ R := by simpa using hwR
      have hwP : w ∉ P := (Finset.mem_sdiff.mp (hw.2.2.2.1 hwR')).2
      change (insert w P).card = 3
      rw [Finset.card_insert_of_notMem hwP, hw.2.2.1]
  | nonempty =>
    obtain ⟨S, hS, rfl⟩ := List.mem_map.mp hl
    exact mem_subsets.mp hS

abbrev EncodedLiteral := Bool × Nat
def encodeLiteral (l : Literal) : EncodedLiteral := (l.positive, varNumber l.var)
def encodedCNF : List (List EncodedLiteral) := generatedCNF.map (List.map encodeLiteral)

def encodedModel (T Q : Family) (n : Nat) : Prop :=
  match variableTable[n - 1]? with
  | some v => model T Q v
  | none => False

theorem encodedModel_varNumber (T Q : Family) (v : Var) (hv : GoodVar v) :
    encodedModel T Q (varNumber v) = model T Q v := by
  have hm : v ∈ variableTable := mem_variableTable.mpr hv
  simp [encodedModel, varNumber, List.getElem?_idxOf hm]

def EncodedSatLiteral (a : Nat → Prop) (l : EncodedLiteral) : Prop :=
  if l.1 then a l.2 else ¬ a l.2
def EncodedSatisfies (a : Nat → Prop) (cnf : List (List EncodedLiteral)) : Prop :=
  ∀ c ∈ cnf, ∃ l ∈ c, EncodedSatLiteral a l

theorem encoded_model_satisfies_cnf {T Q : Family} (h : FiveFields T Q)
    (hne : ∃ S, Q S) : EncodedSatisfies (encodedModel T Q) encodedCNF := by
  intro c hc
  obtain ⟨c₀, hc₀, rfl⟩ := List.mem_map.mp hc
  obtain ⟨o, ho, rfl⟩ := List.mem_map.mp hc₀
  have hw : WellFormed o := by simpa [obligations] using (List.mem_filter.mp ho).2
  obtain ⟨l, hl, hsat⟩ := source_satisfies_clause h hne o hw
  refine ⟨encodeLiteral l, List.mem_map.mpr ⟨l, hl, rfl⟩, ?_⟩
  have he := encodedModel_varNumber T Q l.var (clause_variables_good o hw l hl)
  simpa [EncodedSatLiteral, encodeLiteral, SatLiteral, he] using hsat

theorem encoded_unsat_implies_no_source_model
    (hu : ∀ a, ¬ EncodedSatisfies a encodedCNF) :
    ¬ ∃ T Q : Family, FiveFields T Q ∧ ∃ S, Q S := by
  rintro ⟨T, Q, h, hne⟩
  exact hu (encodedModel T Q) (encoded_model_satisfies_cnf h hne)

end Family156Bridge
