# Family 047: deterministic exact certificate for A[w] ≅ k^[5]

**Finding.** OpenAI's explicit proof that A[w] ≅ ℂ^[5] (prop:stabilization in
*An explicit failure of complex affine-space cancellation*, 23 September 2026)
was checked by full polynomial expansion in ℤ[p,s,u,F,J,M,L,w,E], with no
random evaluation. Every identity it displays holds exactly, as do
con:identity and the H mod p identity of con:domain. The packet also certifies
the two steps the proof argues abstractly:

1. **The exponential automorphism Φ = exp(wΔ).** The packet computes its images
   of the six generators (every division by i! is exact over ℤ), the inverse
   exp(−wΔ), both composites, and Φ(H) = H + p³w.
2. **T = P[w]/(H + p³w) ≅ ℤ[p,s,u,M,E].** The packet checks both round trips.
   One uses an explicit 6,641-term quotient q ∈ ℤ[p,s,u,M,L,w] with
   W(e₀) − w = q·(H + p³w). This replaces the manuscript's cancellation by
   "T is a domain and p ≠ 0".

The [written derivation](PROOF.md) assembles these facts into A_R[w] ≅ R^[5]
for every commutative ring R, because every map has integer coefficients. For
R = ℂ this is the manuscript's stabilization statement. No novelty is claimed.
The other half of the theorem, A ≇ ℂ^[4], is not considered. No manuscript
identity needed correction.

Two implementations agree:
- `check.py` uses the standard library only, with its own sparse integer
  polynomials.
- `independent/independent_check.py` uses SymPy 1.14.0 `ring` over ZZ, with
  its own substitution and division code. A separate Claude agent wrote it.
  The agent had the two manuscript files plus a task specification listing
  the checks to perform, the control mutations, and how to serialize q for
  hashing. It never saw `check.py`.

Both produce the same q, with canonical SHA-256
`a74adf01ee2e0f13c37830a184051da1d706c85b6714704a15157443b4bc97f6`. `check.py`
pins this value as its final check.

## Reproduce

Python 3.13.15. From this directory:

```sh
bash reproduce.sh                  # standard library only
INDEPENDENT=1 bash reproduce.sh    # also the SymPy implementation (needs uv)
```

The script does the following:
- verifies the source hashes;
- runs the 20 unit and integration tests under normal and optimized Python;
- checks that `check.py` prints its 18 checks and that the output is identical
  to the committed `output.txt`;
- runs each of the five negative controls under `python3` and `python3 -O`.
  Each must exit 1 and print `RESULT: fails`.

With `INDEPENDENT=1`, it also reproduces `independent/output.txt` byte for byte,
compares the hash of q with `check.py`'s pin, and runs the independent
implementation's own five controls in both modes.

Expected final line:
`RESULT: family 047 exact certificate and rejection controls reproduced`.
`check.py` takes about 4 seconds. Its stdout is deterministic, because the
runtime goes to stderr. Individual runs:

```sh
python3 check.py                                      # RESULT: holds, exit 0
python3 -O check.py --negative-control e0-sign        # RESULT: fails, exit 1
uv run --no-project --with sympy==1.14.0 python3 independent/independent_check.py
```

| Control | Mutation | Checks that fail |
| --- | --- | --- |
| `H-coefficient` | −2pu instead of −pu in H | 8, then the run stops at p³-divisibility |
| `derivation-value` | ΔJ = 3x²u² + p | Δ-annihilation, Φ(H) |
| `linear-coordinates` | 5s²J instead of 4s²J in M | the linear change |
| `linear-inverse` | 5s²L instead of 4s²L in F(L,M) | 6, then the run stops at p³-divisibility |
| `e0-sign` | +w instead of −w in e₀ | e-certificate, both round trips, hash of q |

A test pins each control's failing checks, so this table cannot drift silently.
Branch coverage of `check.py` is recorded in `logs/coverage.txt`. The only
uncovered line is the `__main__` guard.

```sh
uv tool run --from coverage==7.10.7 coverage run --branch --source=check -m unittest discover -s .
uv tool run --from coverage==7.10.7 coverage report -m
```

## Relation to row 047

Pico's row 047 (`rows/047/check.py` at counterexamples
`f3e88206eb0c1ca065eb7106e06602d1aaa4c25b`) checks the same ten identity groups
at five random 64-bit points. A false identity survives that with probability
at most 4.2·10⁻⁸⁶ (Schwartz–Zippel). The row lists local nilpotency of Δ as not
computed. This packet differs in three ways:

1. It decides the same identities deterministically.
2. It replaces the local-nilpotency and exponential argument with a computed
   inverse automorphism. It still reports the nilpotency indices:
   p:1, s:4, u:2, F:7, J:4.
3. It replaces the domain-based cancellation with the explicit quotient q.

Before writing either check, we read only row 047's docstring, scope and
output, not its identity implementations.

## Scope and limitations

- **What kind of evidence this is.** Exact finite computation plus a short
  written derivation. It is not a kernel-checked proof and not human peer
  review. OpenAI's Lean formalization of this family (`lean/docs/047.md`)
  exists, but was not rebuilt or compared here.
- **Outside scope:**
  - A ≇ ℂ^[4] (manuscript sections 03–06);
  - the irreducibility and dimension arguments of con:domain;
  - any claim about cancellation over rings other than ℂ.
- **Checked by only one implementation.** `check.py` does not check the
  Laurent-ring identities (con:localized-h and the formula for u); the
  independent implementation does. `check.py`'s con:localized-coordinates
  check holds by construction and is recorded only for completeness.
- **Unfinished optional extra.** I started computing the composite map
  A[w] → ℤ[p,s,u,M,E] on the five explicit coordinates Φ⁻¹(p), …, Φ⁻¹(e₀)
  with the standard-library engine, then stopped it after several minutes.
  The step-by-step certificate is already complete without it.
- **Credit.** OpenAI wrote the construction and the argument. Pico, the agent
  operated by Håkon Åmdal, wrote the predecessor check.

## Sources

- **Manuscript:** openai/math commit `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`,
  `preprints/An-explicit-failure-of-complex-affine-space-cancellation-September-23-2026/build/`.
  `source/` holds copies, with `SHA256SUMS` and the Apache-2.0 license:
  - `sections/01-introduction.tex:49-70` (thm:main), SHA-256 `735089761fe6…9540`
  - `sections/02-construction.tex:19-256` (the construction and
    prop:stabilization), SHA-256 `fd10c0e2eb35…a882`
  - `preamble.tex:24`, which defines k = ℂ

  The first two hashes match row 047's pins.
- **Destination:** [piiiico/openai-math-counterexamples](https://github.com/piiiico/openai-math-counterexamples),
  base `f3e88206eb0c1ca065eb7106e06602d1aaa4c25b`. The family is claimed in
  [issue #17](https://github.com/piiiico/openai-math-counterexamples/issues/17).
- **Workspace base:** `130334ce2ce0298f96eaad7f9b0ce5e4ce579d7f`.

## Attribution and status

Alexander Richard Towell, with substantial Anthropic Claude assistance
(Claude Code, Opus 5.5). This is the first Claude pilot in this workspace.
Separate Claude agents wrote the independent implementation and the scoped
review in `REVIEW.md`. AI review is not human peer review.

**Status:** verified locally. The family is claimed in issue #17. The PR waits,
by agreement, until one of PRs #12, #14 or #16 on the destination is resolved.
Related files:
- `visit.json`: time budget and candidate selection
- `LOG.md`: history, including the mistakes I caught
- `verification.json`: receipts
- `HANDOFF.md`: submission steps
