# Family 342: exact all-parameter four-torus algebra

**Finding.** All twenty checked polynomial/exterior-algebra obligations in
OpenAI's four-torus example hold identically. For its original amplitudes,
both the compatible metric and the two taming quadratic forms have lower
bound **1/sqrt(2)**. This supplements the earlier sampled pointwise evidence
with exact algebra over the complete parameter domain. It corroborates the
original example; it does not discover a new counterexample.

The [written derivation](PROOF.md) also records the parameter consequence:
for f=a sin(2 pi x1), k=b sin(2 pi x2), the same construction gives the strict
inclusion for **0<|a|<1 and b!=0**. Compatibility holds for every real a,b;
both fixed forms U±V tame exactly when |a|<1. This is a direct consequence of
the source mechanism, without a global novelty claim.

## Reproduce

Python **3.13.15**, standard library only; no installation is required.
From this directory:

```sh
bash reproduce.sh
```

Expected exit 0, 15 passing unit/integration tests in normal and optimized
Python, twenty polynomial obligations plus the positive numerator check,
and `RESULT: exact all-parameter identities verified`. Three mutated runs
must each exit 1, including under `python -O`. Individually:

```sh
python3 check.py
python3 -O check.py --negative-control eta-factor
```

The second command is expected to reject. Other controls are
`derivative-support` and `taming-amplitude`. Tests independently compare the
Leibniz determinant with rational Gaussian elimination on twenty seeded
integer matrices (seed 342, dimensions 1 through 4). That finite test validates
implementation behavior; it is not the proof of the polynomial identities.

For optional branch coverage:

```sh
uv tool run --from coverage==7.10.7 coverage run --branch --source=check -m unittest discover -s .
uv tool run --from coverage==7.10.7 coverage report -m
```

## Sources and contribution

- OpenAI source commit: `1581d4cbdd69a0faf34b2089614fe2a814316a6a`.
- Example: `preprints/Taming-implies-compatibility-on-four-manifolds-October-6-2026/build/sections/08-cones.tex:375-418`;
  SHA-256 `5b106258d563f938a4ac315a3f3b908698771d2e2d2a196f8449f7406e0974d6`.
- Corrected cone statement: same directory, `01-introduction.tex:61-77`;
  SHA-256 `214bce04a1e697417b8be7c8c9706862c7796e2c9caa3aacb596649f39e51a9d`.
- Counterexamples base: `f3e88206eb0c1ca065eb7106e06602d1aaa4c25b`.
- Workspace base: `90f160d430a87b38309a4efac5dcac6d8225795f`.
- [Coordination and review destination](https://github.com/piiiico/openai-math-counterexamples/issues/13).

OpenAI supplied the construction and qualitative conclusion. Pico, the agent
operated by **Håkon Åmdal**, supplied the prior sampled replay in `rows/342`.
This implementation was derived from the manuscript after reading that
checker's reported scope/header, before inspecting its implementation. The
later predecessor replay is a comparison, not an independent source of the
formulas. Exact sources are included in `source/`, under their Apache-2.0
license; original code and prose are MIT licensed. Preserve both notices.

Contribution by **Alexander Richard Towell** (ORCID 0000-0001-6443-9897), with
substantial **OpenAI Codex** assistance in derivation, code, testing, prose
and one separately tasked scoped AI review.

## Verified scope and limitations

The checker uses canonical sparse integer polynomials in f,k,z. No grid,
floating-point tolerance, finite difference, or heuristic factorization is
used to establish its identities. Positive denominators are cleared using
r>0 and r²=1+f²+k². The inequalities, periodic primitive, Hodge argument and
cohomological obstruction are written mathematics, clearly separated in
PROOF.md; they are not kernel verified. The full general cone theorem and
other manuscript arguments are outside scope. AI review is not human peer
review. Tests and repository acceptance do not establish unrestricted
correctness or novelty. See verification.json and REVIEW.md for exact checks.
