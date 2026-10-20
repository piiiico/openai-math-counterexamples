# A certificate without downward closure

Alexander Richard Towell, with substantial OpenAI Codex assistance.

This follows Pico's [solver observation](https://github.com/piiiico/openai-math-counterexamples/pull/10#issuecomment-6248771785)
that deleting `down` alone leaves the finite ten-label system inconsistent.
The new artifact is a solver-independent RUP certificate for that precise
weakening. It does not claim discovery priority for the observation.
The original certificate, checker, and output remain unchanged.

## Exact proposition

Let \(L=\{0,\ldots,9\}\), and let \(T,Q\) be predicates on subsets of \(L\).
There is no such pair with \(Q\) nonempty satisfying:

1. **tetra_card:** every \(S\in Q\) has four elements.
2. **pure:** every \(U\in T\) is contained in some \(S\in Q\).
3. **no_boundary:** for every \(S\in Q\) and every three-subset \(U\subset S\),
   there is \(S'\in Q\), \(S'\ne S\), containing \(U\).
4. **complementary:** for every \(S\in Q\) and every three-subset
   \(U\subset L\setminus S\), exactly one of \(U\) and
   \((L\setminus S)\setminus U\) belongs to \(T\).
5. **pair_count:** for every \(S\in Q\) and every two-subset
   \(P\subset L\setminus S\), precisely two of the four labels
   \(w\in(L\setminus S)\setminus P\) satisfy \(P\cup\{w\}\in T\).

These are exactly the five remaining fields of
`openai/math@1581d4cbdd69a0faf34b2089614fe2a814316a6a`,
`lean/OAI/Geometry/Borsuk/TenLabels/Labels.lean:13–22`.
The removed field is
`down : ∀ S U, Q S → U ⊆ S → U.card = 3 → T U`.

Crucially, **no_boundary still applies when \(U\notin T\)**. No hypothesis
that \(T\) itself is a simplicial skeleton is inserted after removing `down`.
There is no restriction on the size of members of \(T\) in the source.

## Faithful finite encoding

Restricting any source model's \(T\) to three-element subsets preserves pure
on the remaining members. All complementary and pair-count queries are to
three-subsets, and no-boundary does not query \(T\). Thus any source model
induces a model using only the 120 triple variables and 210 tetrahedron
variables. Conversely a model on those variables extends by taking \(T\)
false on all other subsets and \(Q\) false off four-subsets. Pure then holds
for all subsets, not merely for triples. These maps prove equivalence of
existence for the source statement and the finite encoding.

The direct CNF has:

| Axiom | Clauses | Meaning |
|---|---:|---|
| pure | 120 | A selected triple extends to one of its seven tetrahedra. |
| no_boundary | 840 | For each tetrahedron and each of its four faces, selecting it forces one of the other six extensions. |
| complementary | 4,200 | Each selected tetrahedron enables exactly-one clauses for the ten complementary triple pairs. |
| pair_count | 25,200 | Each of 210 tetrahedra and 15 complement pairs enables eight clauses imposing exactly two of four. |
| nonempty | 1 | The OR of all 210 tetrahedron variables. |

Total: **330 variables, 30,361 clauses**. Cardinality of tetrahedra is built
into the variable domain. Exactly two of four is expressed by a positive
clause for each three-choice subset (at least two true) and a negative
clause for each three-choice subset (at most two true). Implications are
guarded by the negation of the relevant tetrahedron variable.

The 840 original downward-closure clauses are absent. The old fixed-facet
unit is replaced by the unrestricted nonempty clause. **No symmetry
reduction or first-tetrahedron assumption is used.**

`no_down.py` reuses the accepted set-based encoder, removing its labelled
`down` clauses and replacing its nonempty clause. `no_down_independent.py`
constructs the five clause families with label bitmasks, adapting the prior
separate implementation. Their complete clause multisets agree; they share
the stated variable numbering and canonical hash format.

## Certificate and interpretation

`no_down_certificate.json` contains **18,302 RUP additions**, ending in the
empty clause. Glucose4 from `python-sat==1.9.dev6` generated it; the solver's
UNSAT verdict is not accepted as proof evidence on its own.

For each added clause \(C\), the checker negates every literal of \(C\) and
uses unit propagation on the existing clause database to derive a conflict.
Therefore the database implies \(C\). Induction over the additions, ending
in the empty clause, proves the original CNF inconsistent, assuming the
stated encoding and replay algorithms are implemented correctly. Ignoring
solver deletions is sound because previously verified consequences remain
available. The saved SHA-256 bindings prevent accidental use of a stronger
input formula.

The first replay uses the unchanged watched-literal engine `rup.py`; the
second uses the unchanged full-scan bitmask engine from `independent_check.py`.
This is a finite exhaustive logical certificate for the encoded proposition,
not a random search or an inference from failing to find a model. It is
not proof-assistant/kernel verification. The two implementations have shared
predecessors and mathematical assumptions, which are explicitly identified.

The old 327-addition refutation fails at its second addition both against
the new unrestricted weaker CNF and when only `down` is deleted while its
original fixed-facet unit is retained. These failed replays do not refute the
proposition; they explain why a new certificate is needed.

## Reproduction and controls

Python standard library, tested with the version recorded in verification:

```sh
python3 rows/156/finite_obstruction/no_down.py
python3 rows/156/finite_obstruction/no_down_independent.py
python3 -m unittest discover -s rows/156/finite_obstruction -v
python3 -O rows/156/finite_obstruction/no_down.py --negative-control false-clause
python3 -O rows/156/finite_obstruction/no_down_independent.py --negative-control truncated
```

The first command must print
`RESULT: certified finite ten-label obstruction without down`.
Both replays must check all 18,302 additions. The last two commands must exit
one. The full-scan implementation is intentionally slower; its complete
execution, rather than a sampled prefix, is the verification criterion.

On Python 3.13.15, the watched-literal replay completed in 39.249 seconds and
the full-scan replay in 935.900 seconds. All 29 package tests passed.
See [the verification receipt](no_down_verification.json), the
[primary output](no_down-output.txt), and the
[independent output](no_down-independent-output.txt). Times depend on the host.

Optional regeneration uses `requirements-generation.txt` and overwrites only
the new certificate, model controls, and generation receipt:

```sh
python3 -m pip install -r rows/156/finite_obstruction/requirements-generation.txt
timeout 300 python3 rows/156/finite_obstruction/no_down_generate.py
```

The pinned generation rerun reproduced both the certificate and model bytes
exactly. Replay is required after regeneration; generation alone is not proof
acceptance. The default solver heuristics are untrusted proposals, not a search
coverage claim.

Two explicit models in `no_down_models.json` validate further weakenings:

- Remove nonempty: \(T=Q=\varnothing\).
- Remove pure: put \(A=\{0,\ldots,4\}\), \(B=\{5,\ldots,9\}\), and let \(Q\)
  be all four-subsets of \(A\). On \(B\), take the five-cycle with edges
  \(56,68,89,97,75\). Let \(T\) consist of \(\{a\}\cup e\) for \(a\in A\)
  and cycle edges \(e\), together with \(B\setminus e\) for the five
  nonedges of that cycle. These are 30 triples and five tetrahedra.
  Direct semantic checks and clause evaluation verify every retained
  condition and the violation of pure.

Neither control is a counterexample to the five-field proposition. Tests
also ensure no-boundary still triggers with a false triangle variable,
allow nontriple \(T\)-members when their remaining obligations permit them,
and reject altered certificate metadata, a truncated proof, or an unsupported
immediate empty clause. Failure detection remains active under `python -O`.

## Scope, attribution, and review

The topology from a cover to a finite system, the full Borsuk assertion,
Euclidean metric premises, and the source Lean development are not verified
by this supplement. The census classification remains `not-finite`.
No claim is made about deleting additional fields simultaneously.

Credit OpenAI for the source definition and original finite obstruction;
Pico/Håkon Åmdal for the omission observation, independent solver encoding,
and census; the prior Towell/Codex certificate and independent replay for
the reused checking machinery; and Glucose/PySAT for optional generation.
Original supplement code and prose use the existing MIT license.
Substantial OpenAI Codex assistance is disclosed. AI review is distinct
from human review; [the scoped review](NO_DOWN_REVIEW.md) records the specific
checks and shared dependencies. Repository acceptance is recorded separately.
