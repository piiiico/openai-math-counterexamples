/- Copyright (c) 2026 Alexander Richard Towell. MIT license.
Substantial OpenAI Codex assistance. -/
import Family156Bridge

open Family156Bridge Lean

def variableJson (v : Var) : Json :=
  match v with
  | .triangle U => Json.mkObj [("kind", toJson "triangle"),
      ("labels", toJson ((U.sort (· ≤ ·)).map Fin.val))]
  | .tetra S => Json.mkObj [("kind", toJson "tetrahedron"),
      ("labels", toJson ((S.sort (· ≤ ·)).map Fin.val))]

def signedLiteral (l : EncodedLiteral) : Int :=
  if l.1 then (l.2 : Int) else -(l.2 : Int)

def main : IO Unit := do
  IO.println (Json.mkObj [
    ("variables", Json.arr (variableTable.map variableJson).toArray),
    ("raw_obligations", toJson rawObligations.length),
    ("well_formed_obligations", toJson obligations.length),
    ("clauses", toJson (encodedCNF.map (List.map signedLiteral))) ]).compress
