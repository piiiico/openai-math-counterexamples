# Family 049: an integral critical section and all-rings corollary

For the **September 24 companion polynomial** F, this packet gives explicit
integer certificates for a written proof that

`R[h,u,v,w]/(F) ≅ R[X,Y,T]`

over every commutative unital ring R, while F is not an R-coordinate over
any nonzero R, even after adjoining variables. The critical section
`(h,u,v,w)=(2,1,-1,1)` has `F=-1` and all four partial derivatives zero.
Unlike the source's rational point, this section specializes in characteristic
two as well. See [PROOF.md](PROOF.md) for the polynomial and complete argument.

The contribution is a corollary and independent verification of a specified
example. OpenAI's source already states its lifting lemma over arbitrary rings;
Carlos Toledo already supplied an exact integer-polynomial verification of
the complex inverse maps. We add the integral critical section, a compact
generic certificate and explicit coverage of nonreduced base rings. We do not
claim a new complex polynomial, a new lifting theorem, or global novelty.

## Reproduce

Tested with Python **3.10.20**, SymPy **1.14.0**. From this directory:

```sh
python3 -m pip install -r requirements.txt
python3 checker.py --finite-controls
python3 -m unittest discover -s . -v
```

Expected: fourteen zero polynomial residuals over Z, the integral critical
section, all seven finite-ring controls, and the final line
`RESULT: certified integer polynomial identities and integral critical section`.
The 11 tests include subprocess integration and failure controls. The checker
checks coefficients exactly, without random evaluations or field division.

```sh
python3 -O checker.py --negative-control cusp
python3 -O checker.py --negative-control bezout
python3 -O checker.py --negative-control inverse
python3 -O checker.py --negative-control point
```

Each must exit **1**, printing `RESULT: not certified`. They alter, respectively,
a cusp coefficient, a Bezout coefficient, an inverse-map coefficient and the
critical point. Acceptance does not depend on Python `assert` statements.

An optional separate implementation, supplied during the scoped AI review,
uses python-flint **0.9.0** (FLINT **3.6.0**) for the fourteen identities and
standard-library dual arithmetic for derivatives and finite-ring maps:

```sh
python3 -m pip install -r requirements-review.txt
python3 independent_replay.py
python3 -O independent_replay.py --negative-control identity
python3 -O independent_replay.py --negative-control point
python3 -O independent_replay.py --negative-control inverse
```

The first exits 0 with a `RESULT: independent replay passed` line; the three
controls exit 1. This implementation imports neither SymPy nor `checker.py`.
All code and captured outputs are included. Exact commands, versions, exit
codes and file hashes are recorded in `verification.json`.

## Mathematical and computational scope

- The written proof uses equality of explicit ideals and inverse algebra maps;
  it never cancels a possible zero divisor. Its elementary algebra and chain
  rule are written out but are not newly kernel-checked here.
- The primary finite controls exhaust Z/nZ for n=2,3,4,5,6,8,9: 1,681 parameter
  triples and 12,931 ambient quadruples. Both map composites are checked on
  every applicable point, including the entire zero fibre.
- The independent controls exhaust F2[e]/(e²) and F3[e]/(e²), with 64 and 729
  zero-fibre points. These rings have nonzero nilpotents. The finite tests
  supplement the integral proof; they do not prove its universal quantifier.
- The zero ring is allowed for the algebra isomorphism, and excluded from
  the non-coordinate conclusion. The critical point is on F=-1, not on F=0.
- This packet concerns only the September 24 companion. It does not extend
  the October 5 stable-coordinate construction or alter its census status.

## Sources, overlap and credit

The main source is OpenAI's [September 24 companion](https://github.com/openai/math/blob/1581d4cbdd69a0faf34b2089614fe2a814316a6a/preprints/An-explicit-noncoordinate-polynomial-with-affine-three-space-zero-fibre-September-24-2026/build/paper.tex),
lines 87–111 (polynomial), 154–245 (arbitrary-ring lifting lemma), 255–325
(identities and critical-point mechanism), and 345–375 (inverse maps).
SHA256: `60993c0b524291b7f707e42eec89ec7e910c22760d81f1d3af007c229228c13c`.
Its polynomial, lifting method, inverse maps and critical-point obstruction
are credited to the source. The source is Apache-2.0 licensed; a copy of that
license is included as `SOURCE-LICENSE`.

Pico, operated by Håkon Åmdal, supplied the existing Family 049 census check.
Carlos Toledo's [cert-machine F-106](https://github.com/carlostoledo1891/cert-machine/blob/3fabbb80f8a4e9df8c3e623d28259823b4c3a05a/instruments/openaimath/finite/f106_abhyankar_sathaye.py)
already verifies the complex inverse maps in full integer-polynomial
arithmetic. That prior implementation was inspected for overlap, not copied.
The source Lean assembled theorem and critical point were also inspected for
overlap; they use C and the rational point. Generic ring helpers there are
already broader. No source Lean build is claimed. `source-pins.json` records
the exact pins and hashes; this was a bounded overlap check, not a complete
literature or priority audit.

Contributor: **Alexander Richard Towell**, with substantial **OpenAI Codex**
assistance in derivation, implementation, testing and writing. One separate
AI reviewer checked the argument and supplied the independent replay.
AI review is not human peer review; exact computer algebra is not a proof
kernel. New code and exposition are MIT licensed; predecessor attribution
and licenses remain separate. Coordination: [issue 7](https://github.com/piiiico/openai-math-counterexamples/issues/7).
