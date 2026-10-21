/- Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. -/
import Family156Bridge

open Family156Bridge

-- These declarations must be proved without the omitted down field.
#check model_satisfies_generated_cnf
#check encoded_model_satisfies_cnf
#print axioms encoded_model_satisfies_cnf
#print axioms encoded_unsat_implies_no_source_model
#check @encoded_model_satisfies_cnf

example : ¬ Satisfies (fun _ => False) [[⟨true, .tetra ∅⟩]] := by simp [Satisfies, SatClause, SatLiteral]

-- All five fields allow empty families; nonempty Q is an essential extra premise.
example : FiveFields (fun _ => False) (fun _ => False) := by
  constructor <;> simp

example : ¬ ∃ S : Finset Labels, (fun _ => False) S := by simp

-- T is arbitrary on all subsets. The boundary projection does not need T U.
example {T Q : Family} (h : FiveFields T Q) (S U : Finset Labels)
    (hS : Q S) (hUS : U ⊆ S) (hU : U.card = 3) :
    ∃ S', Q S' ∧ U ⊆ S' ∧ S' ≠ S := h.no_boundary S U hS hUS hU

example {T Q : Family} (h : FiveFields T Q) (hne : ∃ S, Q S) :
    ∃ a, EncodedSatisfies a encodedCNF :=
  ⟨encodedModel T Q, encoded_model_satisfies_cnf h hne⟩
