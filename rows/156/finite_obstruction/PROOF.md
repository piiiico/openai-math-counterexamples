# What the finite certificate establishes

Alexander Richard Towell, with substantial OpenAI Codex assistance.

## Precise finite proposition

Let V={0,...,9}, let T be a set of three-element subsets of V, and let Q
be a nonempty set of four-element subsets. The following conditions cannot
hold simultaneously:

1. If S belongs to Q, all four of its triples belong to T (down).
2. Every member of T is contained in a member of Q (pure).
3. For every S in Q and every triple U contained in S, a different member
   of Q also contains U (no boundary).
4. For every S in Q, with C=V\S, exactly one of U and C\U belongs to T
   for every three-element U contained in C (complementary).
5. For every S in Q and every pair P contained in C=V\S, exactly two
   of the four sets P union {w}, w in C\P, belong to T (pair count).

The fixed cardinality of members of Q is the source's sixth `tetra_card`
field. These are precisely the relevant triple/quadruple restrictions of
`OAI.BorsukNine.FiniteObstruction.TenSystem`. Extend T and Q by false on
other cardinalities to recover that structure from a solution here. Conversely,
restriction of any source TenSystem to its triples and quadruples preserves
all five conditions. Its `pure` field does not create an extra premise.

No parity, exact-two tetrahedron multiplicity, short-link classification,
partner-block structure, or conclusion from the manuscript is inserted into
the encoding. In particular, condition 3 only requires at least two incident
tetrahedra. The source's stronger positive-even incidence conclusion implies
this condition, but the finite check does not need that stronger assumption.

## Equivalence with the Boolean formula

Assign a variable t_U to each of the 120 triples and q_S to each of the
210 quadruples. All identifiers are derived from lexicographic combinations;
no manually maintained incidence table is used. Write E(U) for the seven
quadruples containing U. Each condition is encoded as follows:

| Condition | Clauses | Count |
|---|---|---:|
| down | not q_S or t_U, for U contained in S | 840 |
| pure | not t_U or the disjunction of q_S over E(U) | 120 |
| no boundary | not q_S or the disjunction of q_R over E(U) except S | 840 |
| complementary | not q_S or t_U or t_(C\U), and not q_S or not t_U or not t_(C\U) | 4,200 |
| pair count | not q_S or any three of the four t_(P union {w}); also not q_S or their three negations | 25,200 |
| nonempty, after relabelling | q_{0,1,2,3} | 1 |

For four Boolean values, every triple contains a true value exactly when at
most two values are false. Every triple contains a false value exactly when
at most two are true. Taking both families therefore means exactly two are
true. Each guarded family imposes no condition when its q_S is false.
Complementary triples are visited once per unordered complementary pair.

There are 330 variables and 31,201 clauses. Each clause family is equivalent
to the displayed condition, not merely sufficient for it. The only symmetry
normalization is the final unit clause: any nonempty Q has a member S, and
a permutation of V sends S to {0,1,2,3}. All conditions are invariant under
this permutation. No complement system or partner partition is fixed in
advance. Thus unsatisfiability with this unit excludes every nonempty Q.

The domain is all Boolean assignments on these variables, with the displayed
unit fixed. It is not a sampled collection of complexes or a time-limited
failure to find one.

## Refutation and its replay

`generate.py` builds the formula and asks Glucose 4, through pinned python-sat,
for a refutation. `certificate.json` retains its 327 added clauses, including
the final empty clause, and the SHA-256 of the canonically generated DIMACS
formula. Solver output alone is not accepted as evidence of inconsistency.

For each proposed clause C, `rup.py` temporarily assumes every literal in C
is false and performs unit propagation in the original formula plus previously
checked clauses. Acceptance requires a contradiction. Any model of that
database which made C false would survive every sound unit step; therefore a
contradiction proves that the database entails C. Induction on the saved
clauses shows that every accepted clause is implied by the original formula.
Acceptance of the empty clause consequently proves that formula has no model.

The proof generator omits deletion instructions. This is sound: all retained
learned clauses have been proved implied by the original formula. Keeping them
does not remove an original model, and a unit conflict available in a weaker
database remains available when implied clauses are retained. Every addition
is still rechecked against the actual retained database. No RAT-only inference
is silently accepted; any addition that is not RUP fails.

The replay uses two watched literals to implement unit propagation. It does
not import a SAT solver, Lean, external arithmetic packages, or any upstream
proof fragment. An invalid literal, unsuccessful implication check, absent
final empty clause, or premature empty clause rejects the certificate. The
checks are explicit exceptions rather than Python assertions, so optimization
does not disable them. A separate implementation and its precise scope are
recorded in the review receipt.

This is a computational proof of the finite proposition, with a written
encoding argument. It is not a kernel-checked formal proof of the encoding
or of the verifier implementation.

## Controls and complete small-domain checks

The empty family satisfies every condition except nonemptiness. The five
tetrahedral facets of a four-dimensional simplex on labels 0,...,4, with all
their triangle subfaces, satisfy down, pure and no boundary, including the
fixed initial facet; they violate the local complementary-system constraints.
Both assignments are checked against the corresponding weakened formulas.
The saved refutation must fail when replayed against either satisfiable formula.
This guards against vacuous or hardcoded contradiction results.

Additional controls replace the certificate by an unproved empty clause or
truncate it before its final contradiction; both must be rejected. Toy RUP
proofs and literal-domain errors exercise the logical replay separately.

The optional six-label check enumerates all 2^10=1,024 choices of one triple
from each complementary pair. Exactly twelve satisfy the pair-count rule.
For all twelve it verifies the five-cycle links, the four-subset property,
different restricted links, and uniqueness from every five-label restriction.
It checks all 720 permutations: the systems form one orbit, with sixty
automorphisms each. These computations independently corroborate the finite
properties in `six-labels.tex`; the ten-label RUP proof does not assume them.
Flipping one complementary choice in a valid system must fail the pair-count
check. Exhausting this domain is a complete finite check, not a proof about
arbitrary cardinalities.

## Source scope and credit

OpenAI's manuscript derives these finite conditions from a hypothetical
smaller-diameter cover through a smooth admissible map, a symmetric-matrix
extension and topological degree arguments. Those analytic/topological
implications are outside this packet. So are the full projector geometry and
the construction of a finite set of Euclidean points with a covering obstruction.

OpenAI already supplies a written combinatorial proof and a Lean finite-case
development. `TenLabels/Labels.lean` and the initial finite-case file were
inspected; the full Lean development was not rebuilt. This work is an
independent standalone certificate of the finite step, not a new obstruction,
a repair of a claimed missing proof, or an end-to-end verification of Borsuk's
claim. Pico/Håkon Åmdal's existing checker establishes different metric facts
and remains unchanged. Its continuum-witness classification is preserved.

The exact primary source pins and hashes are in `source-pins.json`. New code
and prose are MIT licensed. Source files are cited and hashed rather than
copied or relicensed. Alexander Richard Towell is the contributor; substantial
OpenAI Codex assistance covered formulation, implementation, tests and writing.
Separate AI review is not human peer review.
