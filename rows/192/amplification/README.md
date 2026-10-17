# Family 192: explicit amplification and Boolean-readout budgets

Alexander Richard Towell, with substantial OpenAI Codex assistance.

The earlier packet made one finite observation explicit. This follow-up removes
the remaining unspecified copy counts in that route: **every amplification stage
can use M(n)=2^512 n^2 copies per input**, and the final Boolean readout can use
n^2 copies. The proof applies to deterministic finite observations on n signs
whose retained variance is at least one.

For m=2^24+1 and s=m+1, the complete sign/degree recurrence is

    n_0=D_0=1,
    n_(j+1)=s 2^512 n_j^3,
    D_(j+1)=m 2^512 n_j^2 D_j.

For each integer A>=1, k=4A^2*2^1,442,840,692 stages followed by n_k^2
readout copies give a recursively defined Boolean function whose signed sum
of linear Fourier coefficients exceeds A*sqrt(degree). Its total sign count
is n_k^3 and its degree is at most n_k^2 D_k. The proof specifies exact
conditional-score tables, rational comparisons and tie handling. No unspecified
"sufficiently large" choice remains in this recipe.

These sizes are far beyond feasible evaluation. The packet checks a compact
scalar budget and small exact controls; it does **not** compute the target
Boolean function or formally verify the quantified proof. It is a quantitative
instantiation of OpenAI's existing mechanism, not a new unbounded-violation
theorem. The existing census classification is left for the maintainer to assess.

## Reproduce

From this directory with Python 3.10.20, standard library only:

```sh
python3 checker.py --finite-controls
python3 -m unittest discover -s . -v
python3 -O checker.py --negative-control few-copies
```

The first exits zero with
`RESULT: certified amplification and readout budgets`. All eleven tests pass.
The negative control must exit one. Other rejecting controls are `short-tail`,
`long-tail`, `strong-gain`, `strong-mass`, `few-stages`, and `fourth-moment`.
Rejection means that a sufficient budget failed, not that the construction
with changed parameters is impossible.

`--target A` selects a positive integer target. The iteration count is stored
as a coefficient and a binary exponent; the checker never expands its huge
integer value. The Gaussian checker and certificate are reused only after
checking their pinned SHA-256 hashes. In the public package, the certificate's
relative dependency directory becomes `../gaussian`; no arithmetic changes.

Optional independent replay, with `python-flint==0.9.0`:

```sh
python3 independent_arb.py
python3 -O independent_arb.py --negative-control
```

The first certifies the scalar bounds at 384 bits and checks a separate
asymmetric-score example. The second rejects a false gain demand of 1/5.

## What is new and what is checked

The source already supplies finite observations, amplification, the coarse
reporting rule and Boolean sign readout. The earlier packet's subgaussian
tail estimate does not automatically apply uniformly to later normalized
conditional scores. Here bounded scores give a uniform fourth-moment bound
after the stated averaging count. Truncating CDF comparison at R=2^64 leaves
two tail-error terms equal to 2^-125. The exact scalar gain ratio exceeds
0.026467562004, sufficient for the chosen 1/50 margin at every stage.

The final readout uses Hölder and an exact fourth-moment identity, with no
additional normal-limit argument. A concrete failure control shows why copies
matter: observing whether four signs are all positive gives score variance
16/15 and mean absolute score 1/2, so the proposed universal normalized 1/2
lower bound fails with just one copy. The prescribed 16 copies pass.

Committed exact controls cover 16 fourth-moment identities from four score
laws, 368 normalization comparisons, 336 complete small Boolean truth-table
entries, and 36 small recurrence cases. In one control the ambient dimension
is 6 while the actual degree and bound are 2, checking the distinction relevant
to the theorem. Mutated comparisons, degree accounting and recurrences fail.
These finite controls supplement the written induction and probability proof;
they are not a proof by sampling of the full recursive family.

[PROOF.md](PROOF.md) contains the complete argument and evaluation recipe.
[verification.json](verification.json) records commands, outputs and hashes.
[provenance.json](provenance.json) pins sources and the inherited classical
[Berry--Esseen constant](https://arxiv.org/pdf/1111.6554v1).
[review.md](review.md) records one separate AI review, not human peer review.
No Lean build was performed; the inspected source comparator contains `sorry`
and is not treated as a proved dependency. This does not audit any separate
proof implementation.

## Credit and destination

The canonical destination remains
[counterexamples PR6](https://github.com/piiiico/openai-math-counterexamples/pull/6).
OpenAI receives credit for the underlying reporting/amplification/readout
mechanisms, Pico/Håkon Åmdal for the census and original search, and Irina
Shevtsova for the quantitative classical approximation reference. The earlier
Gaussian and finite-sign packets remain unchanged. New code/prose are MIT
licensed. Substantial OpenAI Codex assistance covered derivation, implementation,
verification and the separate AI review. No global priority claim is made.
