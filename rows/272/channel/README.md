# Family 272: exact trace-preserving channel completion

Alexander Richard Towell, with substantial OpenAI Codex assistance.

**Independent finite verification of an existing construction.** This packet
completes the verified dimension-ten PPT map pair into a trace-preserving
PPT channel \(\Theta:M_{21}\to M_{21}\). It certifies the entire Choi
matrices of \(\Theta\) and \(\Theta^2\), and an exact corner identity with
the tensor predecessor's entangled matrix \(Z_0\).

The generic completion is already proved in the source, Proposition
prop:channel-completion. This is an independently implemented exact
instantiation, not a new normalization theorem or a dimension improvement.
It applies that proposition to our integer-coordinate pair, which is related
to the source pair by the local congruence explained in the tensor packet.
The resulting channel is not asserted to be numerically identical to the
source's orthonormal-coordinate channel.

## Exact findings

Let \(B=D J(\Theta)\) and \(C=D^2J(\Theta^2)\), using the input-first,
unnormalized Choi convention. The certificate stores these integer matrices
as ordered sparse entries.

- Dimension 21; \(D=4,923,191\), \(D^2=24,237,809,622,481\).
- Both source effects have trace 4,923,190.
- \(B,C\) are 441-by-441 matrices, with 6,207 and 11,425 nonzero entries.
- Their exact ranks are 51 and 137.
- Partial traces are \(D I_{21}\) and \(D^2I_{21}\).
- Each matrix is fixed by output partial transpose.
- The entire first-block corner of \(C\) is \(Z_0\): rank 80,
  trace 1,381,419,987,480, and \((0,0)\) entry 40,310,784.
- The positive failure effects have integer Gram witnesses with 6,058
  and 6,780 columns, including the identity summands.
- The absorbing flag gives a positive product eigenvector in the full
  square Choi range. **That full range is not product-free.**

Combined with the tensor/geometry predecessor's proof that \(Z_0\) is
nonseparable, the corner identity proves that \(\Theta^2\) is not
entanglement breaking. The finite checks and the written implication are
distinguished below. No operational secret-key theorem is checked or
claimed, and no proof-assistant or human peer review is claimed.

## Reproduction

Install the pinned requirements in a virtual environment. From rows/272
in the destination repository, the complete dependency chain is:

    python -m rigorous verify
    python -m tensor rigorous/pencil.json
    python -m channel tensor/certificate.json

Expected: all commands exit zero. The last reports status=certified,
dimension 21, denominator 4923191, ranks 51/137 and the rank 80 square corner.
The first two separately verify the geometric and tensor prerequisites.
The channel command does not silently treat a replay as a secret-key proof.

In the original workspace:

    .venv/bin/python -m research.family272_channel research/family272_tensor/certificate.json
    .venv/bin/python -m pytest research/family272_channel -q

The independent replay, which imports no primary checker code, is:

    python channel/review_check.py tensor/certificate.json --channel-certificate channel/certificate.json

Its original-workspace form replaces channel/ and tensor/ by
research/family272_channel/ and research/family272_tensor/.
Both verifiers retain failure detection under Python -O.
The primary complete replay takes about 0.8 seconds on the recorded
environment. See verification.json for commands, versions and exact pins.

## Construction and proof of the finite obligations

Write \(K_{ir}\) for the 36 real integer Kraus matrices of each
dimension-ten map \(\Psi_i\) in the tensor packet. The primary checker
reconstructs the intermediate Kraus matrices from the original integer
pencil, checks the signed exterior complement, and obtains
\[
 A_i=\sum_r K_{ir}^{T}K_{ir},\qquad
 D=1+\operatorname{tr}A_i,\qquad G_i=D I_{10}-A_i.
\]
Equality of the two traces is verified, not imposed on arbitrary PPT pairs.

For every real row vector \(w\), define
\(v_{ij}=w_j e_i-w_i e_j\). Entrywise expansion gives
\[
 \sum_{i<j}v_{ij}v_{ij}^{T}=\|w\|^2I-ww^{T}.
\]
Summing this identity over every row of every Kraus matrix and adding
the identity proves \(G_i=I+\sum vv^T\ge I\).
The checker constructs and multiplies the actual integer Gram factors,
then compares every entry with \(D I-A_i\). This avoids eigenvalue
tolerances and irrational spectral decompositions.

Decompose the 21-dimensional space as two 10-dimensional coordinate
blocks and one flag. With coordinate inclusions \(W_0,W_1\) and flag
projection \(P_*\), define
\[
 D\Theta(X)=
 W_1\Psi_1(X_{00})W_1^T+
 W_0\Psi_2(X_{11})W_0^T+
 \bigl(\operatorname{tr}(G_1X_{00})
       +\operatorname{tr}(G_2X_{11})+D x_*\bigr)P_*.
\]
Off-diagonal input blocks are discarded.

1. **Complete positivity.** Each moving branch has its explicit Kraus
   Gram. The flag branches have the just-verified Gram factors, and the
   last scalar is positive. Equivalently \(B\), after a coordinate
   permutation, is the direct sum of the two positive source Choi
   blocks, \(G_1^T,G_2^T\), and \(D\). Their placement is checked exactly.
   This proves positivity over complex vectors, not merely real ones.

2. **Trace preservation and PPT.** Since \(A_i+G_i=D I\), the displayed
   map preserves trace after division by \(D\). Independently, all
   entries of the Choi partial trace are checked against \(D I_{21}\).
   The verified partial-transpose identities and positivity prove PPT.
   Coordinate transpose is complex linear; it does not conjugate the
   scalar multiplying the flag.

3. **The square.** The primary checker converts the complete \(B\) into
   the 441-by-441 integer superoperator, squares it and converts back,
   using distinct forward and inverse index permutations.
   A separate implementation instead applies the displayed block map
   once and twice to all 441 matrix units. These two methods agree on
   every entry of the saved \(B,C\). Since the matrix units are a
   complex basis, this establishes the map identities for all complex
   inputs. Complete positivity of \(\Theta^2\) follows by composition;
   its partial trace and transpose identities are also checked directly.

4. **Entangled corner.** The absorbing flag never returns to either
   moving block. Thus for every \(X\in M_{10}\),
   \[
   W_0^T\Theta^2(W_0XW_0^T)W_0=D^{-2}\Psi_2(\Psi_1(X)).
   \]
   The entire corresponding Choi corner is checked against \(Z_0\),
   without sampling entries. No dimension factor occurs for the
   unnormalized input-first Choi convention. If the full Choi matrix
   were separable, local compression would make its corner separable,
   contradicting the independently established nonseparability of \(Z_0\).
   Choi separability characterizes entanglement-breaking CP maps.
   This final paragraph is a written argument, not a kernel proof.

5. **Flag qualification.** The computation also proves
   \(C(e_*\otimes e_*)=D^2(e_*\otimes e_*)\).
   This explicitly prevents transferring the predecessor's product-free
   range assertion to the entire channel Choi matrix.

## Failure controls and trust boundary

Tests delete a failure contribution or the flag, corrupt the square, break
partial transpose, alter the source Kraus data, corrupt saved certificates,
and reject malformed sparse matrices. A nonsymmetric tagged-matrix test
checks the forward/inverse index conventions. The independent replay also
rejects a trace-preserving redirected flag, which trace checks alone miss.

The initial primary implementation incorrectly reused the forward
reshuffling as its inverse. Both its trace-preservation test and the
separate reviewer caught this. The corrected full matrices match the
independent direct-map replay. This was a repaired implementation error,
not a defect in the source theorem.

The certificate is deterministic, with no search domain or random seed.
Coverage is all 441 complex matrix units and all matrix entries, plus the
explicit Gram identities. The two channel implementations share FLINT
exact integer arithmetic and the pinned tensor data; algorithmic
independence is not independence of the arithmetic library.
Nonseparability depends on the separate geometry/tensor packet, whose
written bridge is not formalized. The proof does not import the source's
operational claims about protocols or distillable key.

## Provenance and attribution

Source: openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb,
September 27 family 272, build/source/sections/applications.tex,
Proposition prop:channel-completion and equations channel-effects,
channel and choi-corner. That file is unchanged at
1581d4cbdd69a0faf34b2089614fe2a814316a6a.

Destination base after predecessor acceptance:
ed7f37e344741993ca825d3978519cba111fc829.
The work initially began from f8fd99fcb55c044c645083b162af9fd323d189cf
plus the then-open tensor PR. That PR was accepted during this visit.
Tensor predecessor/public PR2 head:
0fce0c35f55bd4bc289d4b6cbb557aec88ea8241.
Its canonical certificate SHA256 is
3fb937f2977c14c6cf840e00a2f9cca9b02db077942c02ccc2ed7e2ac0fff650.
This channel certificate's canonical SHA256 is
e8ce4d253b1e6f9e6d7fd21f3066442269093d52467b17b8756c50d4c88f6c12.

Credit Pico's numerical audit and new manuscript-based tensor cross-check
in ed7f37e, Towell's rigorous geometry and tensor certificates, and the
source authors. Pico's acceptance and independent replay are recorded in
[PR2's review response](https://github.com/piiiico/openai-math-counterexamples/pull/2#issuecomment-6187824166).
The source attributes the two-block
switch to [Christandl, Müller-Hermes and Wolf](https://arxiv.org/abs/1807.01266v2)
and the absorbing trace-preserving extension to
[Filippov](https://arxiv.org/abs/2101.05686v3).
The elementary construction is reproduced here for checkability, not
claimed as our invention.

Apache-2.0; see LICENSE and NOTICE. Substantial OpenAI Codex assistance
covered derivation, implementation, tests, writing and a separately tasked
AI mathematical review. AI review is distinct from human peer review.
