import Controls
import Lean

open Lean Elab Command

/-- Audit all owned declarations, including generated auxiliary declarations. -/
elab "audit_family132" : command => do
  let allowed : Array Name := #[`propext, `Classical.choice, `Quot.sound]
  let env ← getEnv
  let mut reports : Array Json := #[]
  for (name, ci) in env.constants.toList do
    if (`Family132).isPrefixOf name then
      if ci.isAxiom then throwError "Owned axiom: {name}"
      let axs ← Lean.collectAxioms name
      for ax in axs do
        unless allowed.contains ax do
          throwError "Unexpected axiom {ax} in {name}"
      reports := reports.push (Json.mkObj [
        ("name", toJson name.toString),
        ("is_theorem", toJson ci.isTheorem),
        ("axioms", toJson (axs.map Name.toString))])
  if reports.isEmpty then throwError "No owned declarations audited"
  IO.println ((Json.mkObj [
    ("kind", toJson "axiom_audit"),
    ("declarations", Json.arr reports),
    ("count", toJson reports.size)]).compress)

audit_family132

-- The elaborated source-facing type is retained for statement inspection.
run_elab do
  let ci ← getConstInfo `Family132.source_bad_card_le
  let fmt ← Lean.withOptions (fun o =>
    ((o.setBool `pp.fullNames true).setBool `pp.funBinderTypes true).setBool `pp.coercions false)
    (Lean.Meta.ppExpr ci.type)
  IO.println ((Json.mkObj [("kind", toJson "source_statement"),
    ("type", toJson fmt.pretty)]).compress)
