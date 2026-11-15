# Family 132: arbitrary-size XOR-label bound in Lean

Alexander Richard Towell, with substantial OpenAI Codex assistance.

This packet formalizes Lemma A from the existing
[Towell/Claude explicit-labeling supplement](https://github.com/piiiico/openai-math-counterexamples/blob/ea346085fbd714ee5c4d09fc1e899836bc41f3cf/rows/132/explicit_labelling/PROOF.md).
The Lean kernel checks the bound for every finite size and tournament
orientation. This extends Pico's independent finite check through k=24;
it uses the predecessor's dyadic proof, rather than an independent proof method.
No new combinatorial theorem or mathematical novelty is claimed.

## Exact claim

Let S be a finite subset of {1,...,k}, with a tournament orientation R.
Suppose each vertex j has a constant incoming label: there is an m_j such
that every edge i→j inside S has

```
a(i,j) = bit_length((i-1) XOR (j-1)) = m_j.
```

Then |S| ≤ bit_length(k-1)+1. For k>0, bit_length(k-1) is
ceil(log₂ k). The integer expression is the literal formal statement;
identification with the logarithm is explanatory, not a separately formalized
real-logarithm identity. The k=0 case forces S empty.

`Proof.lean` contains:

- `bad_card_le`: a stronger formulation assuming pairwise labels ≤ h.
- `bad_card_le_of_lt_two_pow`: the bound |S| ≤ h+1 for h-bit vertices.
- `bad_card_le_on_range`: zero-based vertices 0,...,k-1.
- `source_bad_card_le`: the actual one-based XOR formula and incoming-label
  witnesses. The indexing shift and preservation of cardinality are checked.

`TournamentOn` requires irreflexivity, completeness on distinct vertices,
and asymmetric orientation. It does not require regularity or an outdegree
bound. `Bad` expresses equality of incoming labels. Its witness equivalence
uses unrestricted natural labels; the manuscript's bounded witnesses imply
this hypothesis directly. Equivalence in the other direction with a bounded
palette also requires a nonempty palette containing all edge labels.

The induction splits on the highest available bit. Equal bits lower the
label bound by one; different bits give the top label. If both halves have
an internal edge, incoming-label constancy forces a cross-edge in both
directions, contradicting the tournament assumption.

## Reproduce

Python 3.10+ with only its standard library; Lean 4.33.1 and Mathlib commit
`0df444a360eaa60ab8c11dca51a86af692955474`. All transitive package revisions
are locked in `lake-manifest.json`. From this directory, with elan/Lake installed:

```sh
lake exe cache get
python3 check.py
python3 -m unittest -v test_check
```

The entry command checks compiler/dependency pins, rebuilds every owned module
in a fresh temporary directory, audits every `Family132` declaration and
checks three deliberately invalid files. It ends with:

```
RESULT: holds — arbitrary-size XOR-label bad-set bound kernel-checked; 3 negative controls rejected; full separation theorem unchecked.
```

Only `propext`, `Classical.choice`, and `Quot.sound` are permitted by the
axiom audit. Owned axioms, `sorryAx`, and additional axioms are rejected.
Warnings are build errors. `output.txt` records the elaborated source-facing
type and declaration audit. Cached Mathlib dependencies are used as the pinned
library environment; this does not rebuild or independently audit Mathlib.

To reuse an existing pinned installation, `python3 check.py --environment
/path/to/environment.json` accepts a JSON object with `compiler` (executable
path) and `LEAN_PATH` (package search path). The same commit/toolchain checks
apply. Only dependency package paths are retained; platform theorem modules
are not imported. No platform source is copied into this packet.

## Controls and scope

`Controls.lean` checks the intended target type, empty/zero-bit cases,
a transitive four-vertex bad set {0,1,3,7} attaining h+1 at h=3,
a non-bad tournament, and a larger bad set for the empty relation.
`negative/FalseBound.lean` must reject the stronger bound h;
`FalseOrientation.lean` must reject the missing completeness assumption;
`OwnedAxiom.lean` must reject an injected axiom through the actual auditor.
The controls use kernel computation (`decide`), not native-decide axioms.
The Python tests cover Lean's nested JSON output and malformed transport.

The manuscript's parameter inequalities, replacement of t=16 by t=h+2,
recurrence interfaces and final sensitivity/block-sensitivity theorem remain
outside the formalization. Sharpness is exhibited at h=3, not proved for all h.
The census status remains `not-explicit`; this packet's RESULT concerns only
the named formalized lemma. Separate AI statement review found no blocker;
it is not human review or an independent Lean implementation.

## Provenance and publication

See `source-pins.json`, `REVIEW.md`, and `CITATION.cff`. The construction and
bad-set definition come from the pinned OpenAI manuscript; the dyadic proof
comes from the credited Towell/Claude supplement. Pico supplied a separately
implemented finite check. This packet's Lean encoding, proof adaptation,
controls and reproduction wrapper were produced by Alexander Richard Towell
with substantial OpenAI Codex assistance. MIT; predecessor attribution
is retained. Publication/acceptance status is recorded separately in the
owning workspace handoff. This is a formal verification supplement, not human
peer review of the paper. No DOI has been minted for this packet.
