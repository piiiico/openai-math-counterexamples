# Family 199: parameter restrictions of the seed resolution

Alexander Richard Towell, with substantial OpenAI Codex assistance.

The displayed seed complex is exact precisely when **q=0 or q has infinite
multiplicative order**, over a field of characteristic two. At a nontrivial
root of order d it first fails in degree d-1. At q=1 it already fails at
the augmentation. At q=0 it remains a resolution, but Ext^n(s,C) has dimension
two for every n>=2, rather than the source's single degree-two class.

These conclusions concern specialization of the specified polynomial table
and differentials. The source assumes transcendental q and is not contradicted.
The result explains why simply choosing q in a finite field does not preserve
the seed mechanism needed downstream. It does not exclude other resolutions,
altered constructions, or finite-field counterexamples.

## Evidence and reproduction

From this directory, with Python 3.13.15 and no third-party dependencies:

```sh
python reproduce.py
```

Expected final line: `RESULT: Family 199 parameter strata, independent oracle
and rejecting controls reproduced`, exit 0. Individual commands are:

```sh
python check.py --report evidence-reproduced.json
python -m unittest -v test_check
python -O -m unittest -v test_check
```

Expected checker result: 1,000 polynomial associativity identities, 30 exact
field/parameter cases, and 710 degrees in each complex; every kernel, image
and proposed homology representative agrees. Expected tests: 12 pass.
The test suite exercises three deliberately false inputs/claims under both
normal and optimized Python. Direct controls, each required to exit 1:

```sh
python check.py --negative-control product
python check.py --negative-control root
python check.py --negative-control zero-dual
```

The first changes ty=q^2 j to ty=qj and fails polynomial associativity;
the others incorrectly demand root-of-unity exactness or the generic dual
profile at q=0, and are rejected by computed homology/cohomology.

`evidence.json` records all q in F2,F4,F8,F16, in coefficient-bit encoding.
The moduli are X+1, X^2+X+1, X^3+X+1, X^4+X+1. Every nonzero element's
explicit inverse is checked. Degrees 0 through 2(|k|-1)+2 are completed for
each q, including the next incoming/outgoing map needed at the endpoint.
The domain and stopping rule are fixed, exhaustive and deterministic; no
random seed or adaptive search is used. This finite replay does not prove
the unrestricted statement: the uniform coordinate proof is in `PROOF.md`.

## Scope, provenance and review

`sources.json` pins OpenAI commit
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`, the source table and Lemma
`res:base`, and the inspected Lean files. Existing `Resolution.lean` already
proves generic exactness under the relevant nonvanishing assumptions. The
addition here is the explicit exceptional homology classification and
independent replay; generic sufficiency is not claimed as new work.

`algebra.json` reuses the table transcription from the predecessor cocycle
packet at `9ce7229089c23e26630850b3c7165a77e9297b85`, accepted in
[PR23](https://github.com/piiiico/openai-math-counterexamples/pull/23).
The binary-polynomial arithmetic and matrix implementation are separate.
The prior cocycle/homotopy archive, DOI
[10.5281/zenodo.23597123](https://doi.org/10.5281/zenodo.23597123), does not
contain this later parameter audit. No old packet or archive is overwritten.

Read `REVIEW.md` and `verification.json` for exact review and test scope.
This is a written proof with exact computational evidence and a separately
tasked AI review, not a new Lean proof or human peer review. At roots of unity,
the dual computation is cohomology of Hom(R,C), **not Ext**, because R is not
exact. D_0 in the evidence is the augmentation defect, not unaugmented H_0.

Coordination: [issue24](https://github.com/piiiico/openai-math-counterexamples/issues/24).
Publication status and continuation are recorded in `HANDOFF.md`.
Source files retain OpenAI's Apache-2.0 license; original code and note use
the included MIT license. See `NOTICE.md` for attribution.
