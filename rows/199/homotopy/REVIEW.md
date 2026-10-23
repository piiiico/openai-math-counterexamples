# Focused review

2026-10-23. One separately tasked OpenAI Codex reviewer inspected the new
written proof, direct tensor implementation and tests against the pinned
source and predecessor definitions. This is AI review, not human peer review.

The reviewer found no mathematical or implementation blocker. It checked
I-balancing, the twisted terminal action, prefix-face cancellation, suffix
p (03-algebra.tex:215–223), and the non-augmented bottom degrees. No additional
projectivity or cocycle-closure premise is needed for the explicit identity.

It separately ran the initial 12 tests, all 17,050 tensor generators, and
7,600 G endpoint action checks, all passing. It also calculated 7,600 B
endpoint action checks and the following corruption witnesses. All four
primary mutation commands exited 1 under optimized Python.

| Corruption | Generator | Nonzero residual |
| --- | --- | --- |
| Omit terminal inverse twist | e[u\|U]e | q(1+H)e[]E |
| Omit H from z | e[u\|j]e | q(1+H)e[]z |
| Remove u from z support | e[x\|u]f | Hq e[]v |
| Set G_1=0 | e[x\|u]f | Hq(x[]u+e[]v) |
| Replace suffix p by prefix p | e[x\|u\|j]e | Hq e[x]z |

The additional prefix-comparison and B-action controls were subsequently
added to the packet tests, together with the inverse-twist right-action
witness q(H+H^2)e[]E. The main author reran the resulting 15 tests.
The first two primary mutations vanish on specializing H=1, illustrating
why the symbolic H check matters. This review shares the inherited algebra
data; it is not a second independent arithmetic implementation or formal proof.
