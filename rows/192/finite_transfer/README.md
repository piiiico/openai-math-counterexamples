# Family 192: an explicit finite-sign observation stage

Alexander Richard Towell, with substantial OpenAI Codex assistance.

The fixed Gaussian schedule in the preceding packet also works when every
Gaussian is replaced by the normalized sum of **N=2^512 independent uniform
signs**. With `m=2^24+1` leaves, the report satisfies

`Var(E[L | report]) > m + Q_N/50`, with `Q_N > 2^(-1,442,840,662)`.

For the sum H of the raw signs, the retained variance is greater than
`mN + N*Q_N/50`. Every report-cell indicator has Boolean Fourier degree at
most `mN=2^536+2^512`; total input cost is `(m+1)N=2^536+2^513` signs.
The scalar lower bound for gain divided by Q_N exceeds **0.026467562004**.
This is an explicit construction in a mathematical sense, not an efficient
algorithm or an enumerated truth table.

This replaces the qualitative finite-input transfer for one fixed schedule
with a concrete sufficient averaging count. The source already supplies the
reporting mechanism, factorization by Q, and qualitative transfer; these are
not claimed as new. Amplification and the final Boolean sign readout remain
unquantified here, and Family 192's full-witness classification remains
**not-explicit**.

## Reproduce

From this packet's directory, with Python 3.10.20 (standard library only):

```sh
python3 checker.py --finite-controls
python3 -m unittest discover -s . -v
python3 checker.py --negative-control small-block
```

The first command exits zero and ends with
`RESULT: certified finite-sign predictor gain > Q_N/50`. The unit tests pass.
The negative control exits **one**, reporting an uncertified sufficient budget.
Additional controls are `short-tail`, `strong-margin`, and `strong-mass`.
A rejected sufficient budget does not disprove that parameter choice.

The certificate pins the unchanged predecessor checker and parameters by SHA-256.
It reuses their exact rational exponential enclosures after checking both hashes.
The only relocation in the public package's certificate is the predecessor
directory (`../gaussian` instead of the archive's `../family192_gaussian`).

Optional independent arithmetic replay, requiring `python-flint==0.9.0`:

```sh
python3 independent_arb.py
python3 independent_arb.py --negative-control
```

The first command certifies the scalar inequalities at 384 bits; the second
rejects the deliberately excessive gain claim `1/5` with exit one. The Arb
implementation uses the formula directly and does not import the main checker.

## Evidence and limits

- [PROOF.md](PROOF.md) derives the CDF, restricted-moment, tail and mean errors,
  the exact deficit identity, and the sign/degree accounting.
- [certificate.json](certificate.json) fixes the one tested successful schedule.
  [checker.py](checker.py) checks sufficient inequalities using exact rationals.
- [finite_controls.py](finite_controls.py) verifies 2,750 weighted small-input
  tuples, 612 interval-endpoint cases and three truncated-second-moment cases.
  A deliberately changed deficit coefficient is rejected. These controls cover
  discrete atoms, selector ties and tails; they are not a proof by sampling of
  the enormous-N statement.
- [verification.json](verification.json) and its logs record fresh execution,
  failure controls, implementation coverage, and the optional Arb replay.
- [review.md](review.md) records one separately tasked AI mathematical review.
  It is neither human peer review nor Lean/kernel verification.
- [provenance.json](provenance.json) records exact source and dependency pins.

The written probability argument inherits the classical iid Berry--Esseen
theorem with constant at most one. Shevtsova's
[Corollary 1, arXiv:1111.6554v1](https://arxiv.org/pdf/1111.6554v1) gives the
stronger constant 0.4748. That theorem is not reproved by the rational checker.
The elementary subgaussian tail bound is proved in the packet. No unrestricted
theorem follows from the finite controls alone.

## Attribution and destination

Credit OpenAI's Family 192 source for the mathematical mechanism and its
qualitative transfer; Pico/Håkon Åmdal for the census and original small-Boolean
search; and Irina Shevtsova for the quantitative normal-approximation reference.
The preceding dyadic Gaussian certificate is Alexander Richard Towell's
AI-assisted contribution in
[PR #6](https://github.com/piiiico/openai-math-counterexamples/pull/6), which is
also this extension's canonical destination. No duplicate PR is needed.

New code and prose are MIT licensed. Substantial OpenAI Codex assistance covered
derivation, implementation, testing and the separate AI review. No global
novelty claim, minimal averaging count or complete Boolean witness is asserted.
