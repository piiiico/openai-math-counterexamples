# What the finite check establishes

Alexander Richard Towell, with substantial OpenAI Codex assistance.
The construction, table, and identities are OpenAI's; this packet contributes
an independent implementation and scoped verification, not a new counterexample.

## Objects and scalar ring

Use the basis, corners and twelve non-idempotent multiplication rules of
`sources/03-algebra.tex:13–34`. The base algebra C has ten basis elements.
The checker constructs T = C ⊕ DC by evaluating the dual actions

    (a φ)(c) = φ(ca),       (φ a)(c) = φ(ac),       (DC)(DC) = 0.

Upper-case letters denote the dual of the corresponding lower-case letter;
their corners are reversed. This is a definition, not an assumption that
dual letters have the same endpoints. The idempotent actions are derived
from the corner data. The scalar ring used by the computation is
R = F₂[q,H,H⁻¹], represented without specialization.

Every polynomial is the finite set of its monomials with coefficient one.
Addition is symmetric difference; multiplication adds exponent pairs and
cancels equal monomials in pairs. Thus an empty set is exactly the zero
Laurent polynomial. Vector operations are the corresponding operations in
the free R-module on the displayed basis. No tolerance or floating point
arithmetic occurs. Python and this implementation remain trusted software.

## Algebra and table checks

The checker verifies associativity on all 20³ basis triples and checks the
trace-dual pairing on all 20² pairs. By trilinearity this establishes the
associativity identity over R. The trace selects the coefficients of E and
F; the computed pairing is λ(a b*) = δ(a,b). Since star is an involution,
this also gives symmetry and nondegeneracy of the trace pairing.

Every nonzero product respects corners and the positive grading of the
source: deg(u)=deg(t)=1, deg(x)=deg(y)=deg(n)=2, deg(v)=deg(j)=3,
deg(z)=4, deg(a*)=5−deg(a), with e,f in degree zero. Therefore the span r of
the other eighteen basis elements is an ideal, r⁶=0, and T/r is the product
of the two scalar rings. After extension to the source field this ideal is
the Jacobson radical. Calling it the Jacobson radical over R itself is not
needed or asserted.

The 179 listed cochain entries are checked for composable radical inputs,
correct output corners, and weight −1, where lower-case weight is zero and
upper-case weight is one. All unlisted values are zero. These checks make
p an I-bimodule map r ⊗ᵢ r ⊗ᵢ r → T, I = Re ⊕ Rf. The source-table
transcription is a separate obligation, recorded in the review and source
hashes; an identity check alone would not establish faithful transcription.

## Complete cocycle and twisted-boundary coverage

For all 18⁴ = 104,976 ordered radical basis quadruples, compute

    a p(b,c,d) + p(ab,c,d) + p(a,bc,d) + p(a,b,cd) + p(a,b,c)d.

Every result is zero. All summands are evaluated linearly when a product
has several terms. Exactly 15,250 quadruples are composable; the computation
also includes every incompatible tuple rather than assuming its residual
vanishes. Multilinearity and I-balancing extend these finite checks to the
whole relative bar term. This proves the displayed cocycle identity,
subject to the stated software and transcription trust boundary.

Let h fix C and scale DC by H. This is an automorphism because DC is a
square-zero ideal and all nonzero products have additive DC weight. Its
inverse scales DC by H⁻¹. Let z(a)=Hqa on
{u,v,t,E,X,Y,Z,U,V} and zero on the remaining radical basis elements.
For each of the 18² = 324 ordered basis pairs the checker directly computes

    Σ_w p(a,b,h(w)) w* + a z(b) + z(ab) + z(a) h⁻¹(b).

The resulting Laurent polynomial vector is zero in every case. This is the
source identity with both sides added, since the characteristic is two.
The implementation does not use the appendix's rearranged constant/linear
coefficient recurrences. Bilinearity covers arbitrary radical arguments.
These identities hold under every scalar specialization into a commutative
characteristic-two field with H invertible. In particular they hold over
F₂(q,H₁,H₂), for H=H₁ and H=H₂.

## The displayed bar cycle

The two words in ζ = q²[t|x|J] + [t|y|J] have both endpoints f. On the
one-dimensional left and right simples at f, every radical letter acts
as zero, so the outer differential terms vanish. The two internal faces
are computed using tx=j, ty=q²j, xJ=T and yJ=q²T. Each of [j|J] and [t|T]
occurs twice with coefficient q², hence dζ=0. The actual checker obtains
this from its derived multiplication table rather than hardcoding the
four products. Its evaluation is

    q²p(t,x,J) + p(t,y,J) = q³f,

which the simple character sends to q³. This is nonzero in the source
field, where q is transcendental (q≠0 suffices for this one conclusion).
The identities still specialize at q=0, but their nonzero evaluation does
not. A test explicitly distinguishes these claims.

For this homological interpretation, first extend scalars to the source
field k=F₂(q,H₁,H₂), with H specialized to H₁ or H₂. The idempotent algebra
Iₖ=ke ⊕ kf is split semisimple. Using its standard relative bar resolution,
a coboundary pairs to zero with every cycle. Thus the
displayed pairing certifies the nonzero evaluated degree-three class.
This last interpretation is a written homological argument, not a separate
machine formalization of projectivity, exactness, Ext, or the bar resolution.

## Failure controls and limits

- Replace p(t,y,J)=q³f by q²f. The cocycle residual at (u,t,y,J) is
  (q²+q³)u.
- Omit h(w) on the left of the boundary identity. At (u,j) the residual
  is q(1+H)z. It vanishes after H=1 specialization, demonstrating why such
  numerical tests would miss this error.
- Replace xJ=T by qT. Associativity at (x,Z,u) has residual (1+q)T.
- A zero cochain satisfies the cocycle equation but does not pass the
  boundary/nonvanishing interface. Tests exercise this vacuity control.

The first three controls exit nonzero under both ordinary Python and
`python -O`; rejection does not rely on `assert`. The seeded arithmetic
oracle tests a declared finite input domain and is not a proof for all
possible polynomial inputs.

This packet does not check the source's later explicit resolution,
all-degree Ext vanishing, cone descent, lifting argument, Tachikawa analogue,
or full Auslander–Reiten counterexample. This is exact finite verification with a written scope
argument and an AI review, not a kernel proof, human peer review, or a
global novelty assessment.
