# Attribution and limitations

Alexander Richard Towell, with substantial OpenAI Codex assistance in derivation,
implementation, verification and writing. One separately tasked AI reviewer
supplied an independent exponent-vector/SymPy finite-field implementation and
examined the source formulas, transcription and code. This is not human review.

OpenAI supplied the manuscript, weights, specialization, tangent, bases and
minor certificates. Classical finite-field linear algebra, polynomial arithmetic
and Schur-complement identities retain their usual attribution. The paper's
references are included. New work is independent reproduction and evidence,
not independent discovery of a hyperbolicity-cone counterexample.

The review implementation shares the source formulas and certificate JSON
for expected minor/basis data. Its source constants were independently read
from TeX, and its polynomial representation and arithmetic library differ.
The coordinating session added canonical hash reporting, without changing
its supplied arithmetic. Dependencies and shared assumptions are disclosed.

Only the finite F7 calculation is audited. Characteristic-zero/real-form
lifting, PSD deformation and final nonliftability remain outside scope.
The raw integer negative principal minor is a boundary control, not a claim
that the source's later real PSD construction is false. No global novelty
assessment or new formal proof is claimed.

New code, data transcription and writing: MIT (LICENSE).
OpenAI source copies: Apache-2.0 (source/LICENSE-openai).
Python, SymPy, mpmath and pytest retain their respective licenses.

Pico’s original repository classification of the whole Family095 claim remains
unchanged; this supplement follows its independent-replay contribution model.
