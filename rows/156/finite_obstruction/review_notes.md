Independent AI review for Alexander Richard Towell, 2026-10-18.

No mathematical or proof-checking blocker was found for the stated finite
TenSystem obstruction. This is a separate OpenAI Codex review and a second
executable check, not human review or a Lean/kernel verification. It does not
verify the geometric or topological bridge to the Borsuk theorem. The source
already contains a finite-case Lean development; no novelty claim is made.

The reviewed proposition is that no nonempty family Q of four-element subsets
of ten labels, with a family T of triples, satisfies the six TenSystem fields.
The source definition and its relabelling lemma were inspected at
[openai/math revision 1581d4cbdd69a0faf34b2089614fe2a814316a6a](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/lean/OAI/Geometry/Borsuk/TenLabels/Labels.lean).
The [six-label section](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/A-nine-dimensional-counterexample-to-Borsuks-covering-assertion-September-23-2026/build/sections/six-labels.tex)
and [ten-label section](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/A-nine-dimensional-counterexample-to-Borsuks-covering-assertion-September-23-2026/build/sections/ten-labels.tex)
were also inspected for the scope of the finite assumptions. The manuscript's
positive-even incidence premise is stronger than the no-boundary condition
used here. Its derived exact incidence, link, and block properties are not
premises of either encoder.

For each selected four-set, the code imposes its four faces, an extension for
every selected triple, another four-set on each face, and the two six-label
conditions on its complement. The six source fields match as follows:

| Field | CNF meaning | Clause count |
|---|---|---:|
| tetra_card | Q variables exist only for four-sets | domain restriction |
| down | Q(S) implies T(U) for every triple U in S | 840 |
| pure | T(U) implies at least one of its seven four-set extensions | 120 |
| no_boundary | Q(S) implies another extension of each face U | 840 |
| complementary | Exactly one of the two complementary triples, guarded by Q(S) | 4,200 |
| pair_count | Exactly two of four extensions of each pair, guarded by Q(S) | 25,200 |
| nonempty anchor | Q({0,1,2,3}) | 1 |

The cardinality clauses are exact: for four variables, every three must
contain a true variable and every three must contain a false variable. These
exclude counts zero, one, three, and four, and permit count two. The guard
means no local six-label condition is required for an unselected four-set.
No assumption says that all ten labels must occur in selected faces.

The anchor does not strengthen the existence question. Any chosen member of
nonempty Q has four labels and can be carried to {0,1,2,3} by a permutation of
the ten labels. Inclusion, cardinality, complements, distinctness, and the
pair counts are preserved. Only this one anchor is used. In particular the
encoding does not normalize a complementary triangle system or constrain a
second tetrahedron.

There is a small type distinction worth making explicit: source T is a
predicate on all finite subsets, with no triangle-card field. Restricting any
source model to its triples preserves all six fields: every non-purity use of
T is on a triple, and purity still holds for every retained member. Conversely
a model with only triple variables extends to the source domain by declaring
T false off triples. Thus the domain restriction loses no possible
countermodel to the obstruction. Nonempty Q already forces nonempty T by down.

The primary watched-literal RUP code was read in full. It copies input clauses,
retains two distinct watched literals in each nonunit clause, moves a watch
only to a literal that is not false, and enqueues a unit only when all other
literals are false. A contradictory enqueue or an empty clause is a conflict.
Persistent watch locations are harmless when a new propagation call clears
the assignments. Tautological clauses and contradictory assumptions behave
soundly. The proof is required to end with a checked empty clause, and an
earlier empty clause is rejected.

Keeping solver-deleted clauses is sound here: each addition is checked by
RUP against the original clauses and previously checked additions. By
induction all retained clauses follow from the original formula. Their
retention cannot create a contradiction in a satisfiable original formula.
No correctness assumption about Glucose, its deletion choices, or its stated
UNSAT result is needed. The generation script's optional appended empty clause
is also checked. The 1,276 ignored deletions in generation.json are generator
metadata; the original deletion transcript was not independently audited.

The second implementation, independent_check.py, imports only the Python
standard library. It generates the axioms using integer masks for label sets,
in a different clause order. Its proof engine uses positive and negative
literal bitmasks and repeated full scans; it shares no propagation or encoder
code with encoding.py or rup.py. The variable convention remains the explicit
lexicographic ordering of triples followed by quadruples so the same saved
certificate can be replayed. Equality of the complete clause multisets was
checked, including multiplicities, after ignoring literal and clause order.

Fresh executable checks completed during this review:

- Independent generation produced 330 variables and 31,201 clauses, exactly
  matching the primary clause multiset.
- Independent full-scan replay accepted all 327 additions and the final empty
  clause; its complete run took approximately nine seconds in this environment.
- Five targeted test methods passed: full certificate replay, clause-multiset
  equality, literal packing/domain rejection, propagation fixtures including
  tautologies, and a two-variable refutation with invalid-proof controls.
  The initial stub implementation failed these tests before implementation.
- All 512 formulas formed from the nine nontautological clauses on two
  variables were tested with all 16 subsets of their four signed literals as
  assumptions. The full-scan checker and one persistent watched database per
  formula agreed in all 8,192 cases. Every one of the 7,744 reported conflicts
  was also checked against all four total Boolean assignments and had no model.
  This tests repeated-call watch state; it is not a general metatheorem about
  the implementation. This enumeration is preserved in review_controls.py.
- With python3 -O, the independent CLI rejected all three negative controls
  with exit status 1. The unsound-clause control proposes not-x1 from the
  satisfiable base (x1 or x2); the false-clause control supplies the empty
  clause immediately for the actual instance; the truncated control removes
  the required final empty clause.
- review_controls.py also rejected its forced-conflict negative control under
  python3 -O with exit status 1, detecting a disagreement on the empty formula.

From this package directory, run the standalone replay with
`python3 independent_check.py`.
Add `--negative-control unsound-clause`, `--negative-control false-clause`, or
`--negative-control truncated` to run the failure controls. Failure controls
are expected to exit 1. The coordinator owns the integrated test suite and
coverage report. The separately added six-system controls are outside this
review's checked coverage.

Run the exhaustive cross-check with `python3 review_controls.py`.
Its `--negative-control` flag deliberately reports a false conflict on the
empty formula and must exit 1. This control script intentionally imports both
engines; the independent replay remains free of primary-tool imports.

The independent replay uses its regenerated formula as the premise; it does
not trust or verify the certificate's order-sensitive cnf_sha256 metadata.
The primary checker verifies that ordered digest. The separately compared
clause multisets and the independent canonical digest identify the common
formula without relying on a shared clause serializer.

Byte-level SHA-256 pins observed in this review:

| Object | SHA-256 |
|---|---|
| Source Labels.lean | 2edf8f16845c943113b43f34542a4bcdd26872910067b35d184c76915882ebb0 |
| Source six-labels.tex | 962e6eb75a7558df8da9fe898ee17c661549368b6b69b9fad7e60d69e0871a71 |
| Source ten-labels.tex | 362fd7d0affd665257e3823779b646b56478d0ed729c33644a10550fa6d2a12c |
| encoding.py | 70a4350279dcca960e1e6be335c0af3003a8a6ff1268bbd9475adb806886f073 |
| rup.py | 508de5602d51235a1eb0f07b8ca2b7f0d35a66d4ebbb5c9dbcb8aeb4f38a37e7 |
| certificate.json | 10d7c6ad10a592b8dbf2f10cfa6dd4144aaff95af9ad1ac36aa4b8c8d924f74a |
| generation.json | db694927ca463e03e7943e6b645be55020dff3856ce294f7401053cff9ec73cb |
| independent_check.py | 58f1b0bf1cc6748d851250aaf3bf782b37c21a7ffc61f09eb9593ab3d3d801cb |
| Primary ordered DIMACS | dc8ed9ef07d0c7671da53a4d529afc6b2230ca7dc1aa08057755ffe2fb1a3cce |
| Independently canonicalized clause multiset | c48bbb7191b7f7f8a1058ac9bf6a1fecfda26cad5d18de6d79c97c620a625f56 |

The canonical digest is SHA-256 of compact JSON for the lexicographically
sorted list of clauses, each clause sorted numerically; duplicates are
retained. Source hashes were computed from the pinned raw GitHub bytes. The
certificate and the primary encoder/proof engine pins above are the objects
on which the conclusion depends. Integration documentation and optional
controls were still being developed by the coordinator during this review.
