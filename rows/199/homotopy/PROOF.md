# A uniform suffix homotopy for the twisted comparison

Alexander Richard Towell, with substantial OpenAI Codex assistance.
This is a written proof, not a kernel-checked formal proof.

## Statement and conventions

Use the algebra T and vertex subalgebra I of the pinned OpenAI source.
Work in characteristic two with H invertible. Write r for the radical,
h for h_H, and P_n=T tensor_I r^(tensor_I n) tensor_I T, for n>=0.
The differential multiplies consecutive factors; P_n=0 for n<0 and d_0=0.
Let Q=P_h, with the same underlying differential and the right action
x dot a=x h(a). A displayed final coefficient b is its underlying value.
The maps below have untwisted targets.

Let p be the source's suffix comparison, and B its appended trace-dual
sum. Assume the finite identity, for all a,b in r,

    sum_w p(a,b,h(w)) w* = a z(b) + z(ab) + z(a) h^-1(b).       (1)

The sum is over radical basis letters and z=z_H is the I-bimodule map
z(a)=Hq a on {u,v,t,E,X,Y,Z,U,V}, zero on the other radical letters.
Its support and value preserve corners. Both h and h^-1 fix I. The
predecessor packet verifies (1) on every radical basis pair, hence by
bilinearity for arbitrary a,b. Its generic coefficient ring is
F_2[q,H,H^-1]; scalar extension gives the source field. Nonzero q is
not needed for this homotopy identity (it is needed for the predecessor's
nonvanishing conclusion).

Define G_0=0, and for i>=1 set

    G_i(a_0[a_1|...|a_i]b)
      = a_0[a_1|...|a_(i-1)] z(a_i) h^-1(b).                  (2)

Then G_i:Q_i -> P_(i-1) are bimodule maps, pi G_1=z', and
pB=dG+Gd in all degrees, where pi:P_0->T is multiplication and
z'(a_0[a]b)=a_0 z(a) h^-1(b).

## Well-definedness and module actions

Tensor balancing at unchanged interfaces is preserved. At the removed
last bar it follows from I-bilinearity of z, and at the final coefficient
it follows additionally from h^-1 fixing I. All products respect their
vertex corners; noncomposable elementary tensors are zero. The formula
is left T-linear. For the twisted right action, replacing b by b h(c)
replaces the output terminal coefficient by z(a_i) h^-1(b) c, precisely
ordinary right multiplication by c. Thus (2) is well-defined and
bimodule linear. Multiplication pi immediately gives pi G_1=z'.

## Cancellation in every degree

It suffices by bimodule linearity to check composable generators with
vertex idempotents at both ends. Fix i>=2 and write a=a_(i-1), b=a_i.
Expand d G_i and G_(i-1) d. The leftmost face and every multiplication
strictly before the pair (a,b) occur once in each expression. Their
outputs agree exactly and cancel in characteristic two. The remaining
terms are

    [a_1|...|a_(i-2)]
      ( a z(b) + z(ab) + z(a) h^-1(b) ).                      (3)

The first comes from the final differential face of G_i; the second
from the penultimate face of d; the third from the final face of d,
using the source-to-target extension by h^-1. If ab is a sum of radical
letters, z(ab) is understood linearly. Radical closure ensures it is
defined. At i=2 the prefix is empty, retaining its left vertex.

On the other hand, applying B_i first appends h(w) and terminal w*.
The suffix comparison p then removes the last three bars a,b,h(w).
Consequently (pB)_i is precisely the prefix in (3) followed by
sum_w p(a,b,h(w))w*. Equation (1) proves equality. Vertex restrictions
introduce no omitted nonzero terms because p, multiplication and z
preserve corners.

For i=0, B_0 has degree1 and p is zero there; G_0 and all negative
targets are zero. For i=1, B_1 has degree2 and p is again zero;
d_0 G_1=0 and G_0 d_1=0. These cases use the unaugmented convention:
pi is not d_0. This proves the assertion in every degree.

## Scope

This makes the choice in source Lemma lift:G explicit. Its recursive
projectivity argument was already a valid existence argument; no gap
or new counterexample is alleged. The proof uses the finite boundary
identity directly and does not require a separate cocycle-closure
argument for this equality. The source's other cone components, stable
category passage, resolution, Ext assertions and complete
Auslander–Reiten counterexample remain outside this contribution.
Classical bar-complex cancellation is the method; no global novelty claim
is made. Finite tensor replay is supporting evidence, not the all-degree
proof. One AI review is not human peer review.
