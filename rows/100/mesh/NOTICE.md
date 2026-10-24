# Attribution and licensing

Alexander Richard Towell developed this packet with substantial OpenAI Codex
assistance in derivation, code, tests and writing. One separately tasked AI
review concerns geometry, hidden hypotheses and complete costs; it is not
human peer review.

OpenAI's *Finite angular cylinder covers below the half-area bound* supplies
the parabolic secant construction, first-crossing mechanism, radial identity,
projection normalization and Taylor/integral area argument. The contribution
retains the mesh width in those estimates and extends them to arbitrary finite
partitions. It independently implements the algebra and parameter checks; the
manuscript is the mathematical predecessor, not an uncredited new mechanism.
Pinned extracts retain Apache-2.0; their license is in source/LICENSE-openai.

Pico (an AI agent operated by Håkon Åmdal) previously checked the source's area
and sampled coverage in rows/100/check.py. Its scope docstring was read during
selection; this packet does not reuse its implementation. Ricardo Pinho's
separate optimized 4096-cylinder construction and exact coverage certificate
are stronger existing results, with their own authorship and AI disclosures:
https://github.com/rpinho/tetrahedron-cylinder-cover/tree/2e648347ddd2c76e0fcb46ce67d8238684e29d03
Earlier Towell/Codex structural-radius audits concern that optimized family,
not this source-family mesh criterion. They are not repeated here.

New checker, proof and tests are MIT (LICENSE). SymPy and mpmath remain under
their respective licenses and authorship. Verification, repository acceptance,
novelty assessment and DOI publication are distinct; none implies the others.
