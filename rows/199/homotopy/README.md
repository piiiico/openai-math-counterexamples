# Family 199: an explicit twisted bar homotopy

Alexander Richard Towell, with substantial OpenAI Codex assistance.

The source proves existence of G by successive projective lifts. Here one
uniform formula supplies those maps: remove the final bar letter and place
its z_H value in the terminal coefficient, with the prescribed inverse twist:

    G_i(a_0[a_1|...|a_i]b)
      = a_0[a_1|...|a_(i-1)] z_H(a_i) h_H^-1(b),  i>=1; G_0=0.

[PROOF.md](PROOF.md) proves pB=dG+Gd in every degree, including 0 and 1,
from the previously verified finite boundary identity. It checks I-balancing
and the twisted bimodule action. This makes one component of the source's
cone-lift construction directly computable. The original existence argument
is not alleged to be defective.

## Reproduce

Python 3.13.15, standard library only:

```sh
python3 research/family199_homotopy/reproduce.py
```

In the destination checkout use `python3 rows/199/homotopy/reproduce.py`.
Expected exit 0 and final line:
`RESULT: Family 199 explicit homotopy replay and rejecting controls reproduced`.

The command checks eight source/dependency hashes, reruns the inherited finite
algebra/cocycle/boundary certificate, and independently expands pB and dG+Gd
as sparse tensors over F_2[q,H,H^-1]. It exhausts all 17,050 composable bar
generators in degrees 0–4 and 7,600 left/right G action equalities in
degrees 0–2. Four incorrect G formulas must fail under both ordinary and
optimized Python. Tests include the non-augmented bottom degrees and d^2=0.

## Scope and dependencies

Source: `openai/math@1581d4cbdd69a0faf34b2089614fe2a814316a6a`,
`06-lift.tex`, Lemma `lift:G`; suffix p is in `03-algebra.tex` and z/its
boundary equation in `09-cochain.tex`. Exact file hashes: [sources.json](sources.json).
H is invertible, the coefficient characteristic is two, and h fixes I.
Nonzero q is unnecessary for this identity. The frozen dependency is the
earlier Family199 contribution at `9ce7229089c23e26630850b3c7165a77e9297b85`,
archived as [v1.0.0](https://doi.org/10.5281/zenodo.23592160).

The tensor implementation is new; its polynomial arithmetic and algebra/data
are explicitly reused from that dependency. It is not a wholly independent
algebra implementation. Finite replay supports the written general proof;
neither is Lean/kernel verification or human peer review. The complete
resolution, stable-category argument, Ext vanishing, and full
Auslander–Reiten counterexample remain unchecked. See [NOTICE.md](NOTICE.md)
for predecessor credit and component licenses.
