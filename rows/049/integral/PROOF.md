# The companion's integral model and critical section

Alexander Richard Towell, with substantial OpenAI Codex assistance.

This isolates an all-rings corollary for the September 24 Family 049
companion's specified polynomial. The polynomial, lifting mechanism and
zero-fibre maps are the source's; its lifting lemma already explicitly allows
arbitrary commutative rings, including zero divisors. The added observation
used here is an integral critical section, paired with a separate exact
verification of the generic lifting identities. A written proof and exact
polynomial certificate are supplied, not a Lean proof or human peer review.

## Statement

In `Z[h,u,v,w]`, define

\[
\begin{aligned}
x&=u^3+hv,& y&=-u^2+hw,\\
s&=2u^3v+3u^4w+h(v^2-3u^2w^2)+h^2w^3,\\
p(x,y,s)&=-2s^2x+3sy^2-3s^3y,& F&=h-p(x,y,s)-1.
\end{aligned}
\]

For every commutative ring `R` with identity, the specialization of `F`
satisfies

\[
R[h,u,v,w]/(F)\cong_R R[X,Y,T]. \tag{1}
\]

If `1_R != 0_R`, then `F` is not an `R`-coordinate: no `R`-algebra
polynomial automorphism has `F` as a component. This remains true after
adjoining any finite number of independent variables. There is no assumption
that `R` is a field, domain, reduced, or of characteristic zero.

The zero ring is allowed in (1), but excluded from the non-coordinate claim.
This concerns only the September 24 companion. It says nothing about the
October 5 stable-coordinate polynomial's small-characteristic behavior.

## Division-free lifting lemma

Let `B` be a commutative unital ring with elements `h,x,y,s,alpha,beta`
satisfying

`D=x^2+y^3-hs=0` and `E=alpha*h+beta*y-1=0`.

Let `S(h,U,V,W)` be the polynomial defining `s` above and set

\[
C=B[U,V,W]/(U^3+hV-x,\ -U^2+hW-y,\ S(h,U,V,W)-s).
\]

Then `C` is `B`-isomorphic to `B[T]`.

Put `G=V+UW`, with polynomial inverse `V=G-UW`, and write

\[
\begin{aligned}
g_1&=hG-yU-x, & a&=y+U^2, & b&=s-hG^2+2UyG,\\
g_2&=hW-a, & g_3&=y^2W-b.
\end{aligned}
\]

The identities

\[
\begin{aligned}
U^3+h(G-UW)-x&=g_1-Ug_2,\\
S(h,U,G-UW,W)-s&=g_3+g_2(-2UG+2yW+Wg_2)
\end{aligned}
\]

show equality of the two defining ideals: each displayed correction is a
multiple of the unchanged second relation `g_2`. Hence
`C = B[U,G,W]/(g_1,g_2,g_3)`.

Work next in `A=B[U,G]/(g_1)`. The identity

\[
y^2a-hb=D+g_1(hG-yU+x)
\]

gives `y^2a=hb` in `A`. Set
`r=alpha*(1+beta*y)`, `q=beta^2`, `W0=ra+qb`.
The exact identity `rh+qy^2-1=E(1+beta*y)` gives `rh+qy^2=1`.
Consequently

`hW0=a`, `y^2W0=b`, and `W-W0=r*g_2+q*g_3` in `A[W]`.

Conversely `g_2=h(W-W0)` and `g_3=y^2(W-W0)`. Thus the ideal
`(g_2,g_3)` is exactly `(W-W0)`, including when `h` and `y` are zero
divisors. Eliminating `W` gives `C` isomorphic to `A`.

Finally, the maps

\[
U=hT-\beta x,\qquad G=yT+\alpha x,\qquad
T=\alpha U+\beta G
\]

are inverse `B`-algebra maps between `A` and `B[T]`. The following free
integer polynomial identities explicitly verify well-definedness and both
composites:

\[
\begin{aligned}
h(yT+\alpha x)-y(hT-\beta x)-x&=xE,\\
\alpha(hT-\beta x)+\beta(yT+\alpha x)-T&=TE,\\
h(\alpha U+\beta G)-\beta x-U&=UE+\beta g_1,\\
y(\alpha U+\beta G)+\alpha x-G&=GE-\alpha g_1.
\end{aligned}
\]

No division or cancellation of a ring element occurred. In particular,
injectivity of multiplication by `h`, `y`, 2 or 3 was never assumed.

## The integral zero fibre

Use the auxiliary algebra

`B=R[h,x,y,s]/(H,D)`, where `H=h-1-p(x,y,s)`.

Set

\[
\alpha=1+2s^2x+4s^5,\qquad
\beta=(3s^3-3sy)(1+2s^2x)-4s^4y^2.
\]

The integer Bezout identity

\[
\alpha h+\beta y-1=(1+2s^2x)H-4s^4D
\]

supplies the lifting lemma's unit-ideal condition over every `R`.
Eliminate `h` using the monic relation `H`, and make the polynomial change
`X=x+s^3`, `Y=y-s^2`, whose inverse is `x=X-s^3`, `y=Y+s^2`.
The exact shift identity

\[
X^2+Y^3-s=D+sH
\]

then eliminates `s` by `s=X^2+Y^3`. Thus `B` is isomorphic to `R[X,Y]`.
These are eliminations of variables with unit coefficient, so no domain,
flatness or characteristic restriction is needed.

Apply the lifting lemma over `B`. In the combined presentation of `C`,
the three lifting equations eliminate `x,y,s`, leaving `R[h,u,v,w]`.
The source cusp identity `x^2+y^3=hs`, checked over `Z`, makes `D` vanish
identically. The remaining relation `H` becomes exactly `F`. Therefore

`R[h,u,v,w]/(F) = C ≅ B[T] ≅ R[X,Y,T]`.

For direct use, the maps are:

- From the zero fibre: `X=x+s^3`, `Y=y-s^2`,
  `T=alpha*u+beta*(v+u*w)`.
- From `R[X,Y,T]`: first `s=X^2+Y^3`, `x=X-s^3`, `y=Y+s^2`,
  `h=1+p(x,y,s)`; form `alpha,beta` as above, then
  `u=hT-beta*x`, `g=yT+alpha*x`,
  `w=alpha*(1+beta*y)*(y+u^2)+beta^2*(s-h*g^2+2u*y*g)`, `v=g-u*w`.

All coefficients are integers. The lifting proof verifies the maps in the
quotient, including all fibres where `h=0`; a generic-point calculation alone
would not justify (1).

## An integral critical section

At the integral point `P=(h,u,v,w)=(2,1,-1,1)`, direct substitution gives

`x=-1`, `y=1`, `s=1`, `p=2`, `X=Y=0`, and `F=-1`.

The ambient identity `X^2+Y^3=s(1+F)` follows from the cusp and shift
identities. Formal differentiation over `Z` gives

`2X dX + 3Y^2 dY = (1+F) ds + s dF`.

At `P`, this reduces to `dF(P)=0`, with no division. The checker also
expands `F` and evaluates all four formal partial derivatives directly at
`P`, independently of this differential argument. These integer identities
specialize to every commutative `R`, including characteristic two, where
the point becomes `(0,1,1,1)`.

If an `R`-algebra polynomial automorphism had `F` as a component, its
Jacobian at `P` would have a zero row. The chain rule applied to the
automorphism and its polynomial inverse says this matrix is invertible.
A zero row cannot occur in an invertible matrix over a nonzero unital ring:
multiplication by an inverse would give a zero row in the identity matrix.
This contradiction proves non-coordinateness. Added variables have zero
partial derivative and can be set to zero at `P`, proving the stabilized
non-coordinate assertion as well.

## Verification scope and credit

The checker verifies fourteen free polynomial identities over `Z` and the
integral critical-section data. These finite coefficient computations support
the written universal-ring proof; finite-ring controls are not an inference
from tested characteristics to all characteristics. SymPy is trusted software,
not a proof kernel. The statement also relies on elementary quotient-ring
maps and the polynomial chain rule as explicitly written above.

The polynomial, generic lifting method and inverse maps are from OpenAI's
September 24 companion, pinned at
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`,
`preprints/An-explicit-noncoordinate-polynomial-with-affine-three-space-zero-fibre-September-24-2026/build/paper.tex`.
Pico/Håkon Åmdal checked the complex example in the counterexample census.
Carlos Toledo's cert-machine F-106, pin
`3fabbb80f8a4e9df8c3e623d28259823b4c3a05a`, already verifies the complex
inverse maps using integer polynomial arithmetic; that prior computation
supports the base-change perspective and is explicitly credited.

The same OpenAI commit's Lean `AbhyankarSathaye/CriticalPoint.lean`,
`NonCoordinate.lean`, `Fiber.lean` and `Counterexample.lean` were inspected.
Its generic critical-point and chain-rule helpers already allow arbitrary
commutative rings, while its specified point uses halves and its assembled
counterexample is over the complex numbers. Those source helpers are not
claimed as new here. We did not rebuild or audit the source Lean development.

The present contribution isolates the universal-ring statement, verifies its
generic division-free lifting obligations in a different implementation,
and supplies the integral critical section. It does not claim a new complex
polynomial, priority for a positive-characteristic counterexample, or global
novelty of this straightforward extension.
