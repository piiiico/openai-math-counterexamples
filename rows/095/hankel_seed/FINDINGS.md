# What the finite certificate establishes

Alexander Richard Towell, with substantial OpenAI Codex assistance.

## Reconstruction and exact agreement

The source is Appendix A of the October 5 *Hyperbolicity Cones Without
Semidefinite Lifts* manuscript, pinned in sources.json. All calculations here
use its weights modulo ten, point a=(1,6,6,0,3,0,2,5) modulo seven, specified
pivot columns and 35 tangent moments. Monomials are generated from definitions
and checked against the printed ordered lists.

The seed T is the 36×36 matrix t(uv), with t(m)=1+m(a) for weight-zero quartics
and zero otherwise. Its rank is 20, its L restriction has determinant 6, and
its 16-column J basis agrees with every displayed basis column. N has 28 columns.
The full equations TJ=0, JᵀT1J=0, TJ'+T1J=0, T(L,N)=0 and the differentiated
last equation vanish entry by entry. These checks validate the derivative
formulas outside the chosen pivot rows as well as on those rows.

For each weight, ordinary polynomial products assemble G1, G2, D and D1 with
the source's column order. No multiplicity-two normalization is introduced for
unordered symmetric-product columns. All six G1, G2, E and Z determinant values
match, as do all 21 displayed corner entries. Six directly evaluated bordered
minors also match E's determinant squared times Z's determinant in the stated
ordering. The full modular ranks are:

| Weight | G1 | G2 | D | Bordered |
|---|---:|---:|---:|---:|
|0|17|8|32|65|
|1|11|8|28|58|
|2|16|9|32|66|
|3|11|8|29|60|
|4|16|9|32|66|
|5|11|8|28|58|
|6|16|9|32|66|
|7|11|8|29|60|
|8|16|9|32|66|
|9|11|8|28|58|
|Total|136|84|302|623|

Weights six through nine hold at this very specialization; their computation
is separate from the source's genericity/permutation argument. The difference 623-2·302=19 checks the finite first-order increment. No search was run:
the entire prescribed finite object was reconstructed deterministically.

For the direct bordered minors, the primary row order is top R, bottom R,
bottom R', and the column order is left S, right S, left S'. This makes the
Schur-complement determinant identity exact. The independent implementation
uses left S, left S', right S and includes its permutation sign. Here the signs
are positive because every |R|·|R'| is even. Both give 5,5,6,2,4,4.

## Boundary control: no explicit real PSD witness

Consider the naive raw matrix obtained by evaluating the same moment formula
at the printed integers without modular reduction. For u=x0x2 and v=x0x3,
the weights of u² and v² are 2 and 8 modulo ten, so both diagonal entries vanish.
Their product has weight zero, but a2a3=6·0=0, giving off-diagonal entry 1.
The 2×2 principal block is therefore [[0,1],[1,0]], determinant -1.
It is not PSD as a real matrix in this raw coordinate basis.

This is not a source contradiction. The appendix first works in complex
coordinates, then uses a conjugate-pair real form and genericity to obtain
simultaneous real PSD data. The printed specialization a2=6,a3=0 is not in
that real form. The calculation exposes an invalid shortcut—treating the
printed modular/rational point as the final real PSD witness—without contesting
the stated lifting argument.

## Verification boundaries and interpretation

This packet establishes agreement of a complete finite replay, supported by
a separately implemented finite-field oracle and corruption controls. The
new work supplies portable independent executable evidence for the seed
calculation. It does not reprove the passage to characteristic zero, simultaneous
real data, smooth PSD deformation, separation/moment obstruction or nonliftability.
The finite data are not a kernel proof or human peer review. No global novelty
claim is made, and the overall family classification remains not-finite.
