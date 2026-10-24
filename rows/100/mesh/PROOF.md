# Coverage and area with an explicit mesh bound

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written proof with exact algebra checks; not a formal proof or human peer review.

## Statement and provenance

Use physical coordinates (x,y,Ht), H=sqrt(2), and the regular tetrahedron
K={0<=t<=1, |x|<=1-t, |y|<=t}. Fix any finite strictly increasing partition
-1=q_0<...<q_n=1. Let h_j=q_(j+1)-q_j and D=max h_j. For each interval [l,r], set

    alpha=(1+lr)/4, beta=(l+r)/4,
    d(q)=q^2(1+q^2)/16,
    M=eta+max(d(l),d(r)), T=1/2+tau^2 M.

The maximum is exact because d is even and increasing with |q|. The lower
intercept triangle is {(0,y0,Ht0):0<=t0<=T, l t0<=y0<=r t0}, with axis
(1,tau alpha,H tau beta). The upper triangle is
{(x0,0,H(1-s0)):0<=s0<=T, l s0<=x0<=r s0}, with axis
(-tau alpha,1,H tau beta). A cylinder is the triangle plus the full real span
of its axis. The two families use the same partition and per-sector cutoff.

**Coverage criterion.** For 0<tau<1 and eta>=0, all 2n cylinders cover K if

    G(tau,eta,D)=2eta-(7/4+2eta)tau-D/(4tau)-D/4 >= 0.       (C)

**Area criterion.** For 0<tau<1 and 0<=eta<=1/8, their total perpendicular-base
area, divided by the minimum projection area of K, satisfies

    |C - 1/2 - (2eta-1/240)tau^2| <= 59tau^4/64 + tau^2 D. (A)

These conclusions do not require D<=tau^2 or a uniform partition. Their proofs
retain the mesh error in OpenAI's coverage and area argument instead of making
that substitution. This is a small parameter/general-partition refinement,
not a new coverage mechanism. Source pin and exact extracts are in sources.json.
Pinho's separate 4096-cylinder construction uses a different optimized phi and
has much stronger saving; no best-known or global novelty claim is made here.

## Angular membership, including the boundary

For each interval the two exact identities
alpha-l beta=(1-l^2)/4 and alpha-r beta=(1-r^2)/4 hold. Also
0<=alpha<=1/2, |beta|<=1/2 and eta<=M<=eta+1/8.

Fix (x,y,Ht) in K and s=1-t. Define
F_i=q_i t+tau x(1-q_i^2)/4. Then F_0=-t<=y<=t=F_n.
Choose the first i>=1 with F_i>=y and put j=i-1. For i=1,
F_j<=y by the endpoint condition; otherwise minimality gives F_j<y.
The sequence need not be monotone. The two inequalities are exactly

    l t0<=y0<=r t0, t0=t-tau x beta_j, y0=y-tau x alpha_j.

Subtracting the outer terms gives h_j t0>=0, hence t0>=0. Thus this lower
cylinder contains the point unless t0>T_j. Equality at the radial boundary
counts as covered. The same first-crossing argument for
G_i=q_i s-tau y(1-q_i^2)/4, with endpoints -s and s bracketing x, gives

    l' s0<=x0<=r' s0, s0=s+tau y beta_k, x0=x+tau y alpha_k,

and s0>=0. The upper cylinder contains the point unless s0>T_k.
No assumption about monotonicity of either sequence or interior position of
the point has been made.

## Excluding simultaneous radial failure

Suppose both selected cylinders miss. Then

    a=t0-1/2 > tau^2 M_j >=0, b=s0-1/2 > tau^2 M_k >=0.

Write q=y0/t0 in the lower interval and p=x0/s0 in the upper interval.
Because |x|+|y|<=1 and |beta|<=1/2,

    t0+s0=1-tau x beta_j+tau y beta_k <=1+tau/2.

Consequently 0<a,b<=tau/2. From y=t0 q+tau x alpha_j and
x=s0 p-tau y alpha_k we obtain |y-q/2|<=tau and |x-p/2|<=tau.
The exact radial identity is

    a(1-tau xq)+b(1+tau yp)
      =tau^2(x^2 alpha_j+y^2 alpha_k)
       -tau x(beta_j-q/2)+tau y(beta_k-p/2).             (R)

To verify it directly, use a+b=-tau x beta_j+tau y beta_k,
qa=y-tau x alpha_j-q/2 and pb=x+tau y alpha_k-p/2;
the mixed xy terms cancel. The checker independently substitutes the intercept
formulas into (R) and simplifies the full rational expression to zero.

For every q in [l,r], |beta_j-q/2|<=h_j/4<=D/4, and likewise for p.
The factors multiplying a,b in (R) are at least 1-tau>0. Therefore strict
failure forces

    0 > (M_j+M_k)(1-tau)-D/(4tau)
        -(x^2 alpha_j+y^2 alpha_k).                    (F)

Indeed, the absolute value of the two last terms in (R) is at most
 tau D(|x|+|y|)/4<=tau D/4, and division by tau^2 is valid.

Next |x^2-p^2/4|<=3tau/2 because |x|<=1 and |p|<=1; similarly for y,q.
For q in [l,r],

    |alpha_j-(1+q^2)/4|<=D/2.

For example, |lr-q^2|=|l(r-q)+q(l-q)|<=h_j already gives the stronger
h_j/4 bound after division by 4; we retain the source's looser D/2 constant.
It follows, using alpha<=1/2 and p^2,q^2<=1, that

    x^2 alpha_j+y^2 alpha_k
      <= (p^2+q^2+2p^2 q^2)/16+3tau/2+D/4
      <= d(p)+d(q)+3tau/2+D/4.

The last difference is exactly (p^2-q^2)^2/16>=0. Furthermore
M_j+M_k>=2eta+d(p)+d(q). Put E=d(p)+d(q)<=1/4.
The right side of (F) is at least

    (2eta+E)(1-tau)-D/(4tau)-E-3tau/2-D/4
      = G(tau,eta,D)+tau(1/4-E) >= G(tau,eta,D).

Thus (C), including equality, contradicts strict simultaneous failure.
The proof covers every point of the closed tetrahedron, not just a mesh.
It also covers all sector boundaries without selecting a unique cylinder.

## Normalization and complete area cost

The four outward face area vectors of K are (0,+/-H,-1), (+/-H,0,1).
For a physical unit direction u, forward-facing triangles partition its
shadow up to boundaries. Projection of a face has area |N dot u|. Since
these four vectors sum to zero, the projection area is half the sum of
absolute scalar products, hence

    A(u)=max(H|ux|,|uz|)+max(H|uy|,|uz|).

Put U=max(|ux|,|uz|/H), V=max(|uy|,|uz|/H). Then
(U+V)^2>=ux^2+uy^2+2uz^2/H^2=1. Thus A(u)>=H, with equality
at u=(1,0,0). The normalization is exactly A_min(K)=H.

Project each intercept triangle perpendicular to its axis. Its axis has a
nonzero normal component (equal to 1) relative to the intercept plane, so
projection is injective there and preserves the cylinder after adding the
axis span. Each perpendicular base is a compact nondegenerate triangle.
Both families together contribute exactly

    C=sum_j h_j (1/2+tau^2 M_j)^2 / sqrt(1+tau^2 A_j),
    A_j=alpha_j^2+2beta_j^2.

No triangle, second family, or projection factor is omitted. Here 0<=A_j<=1
and, for eta<=1/8, 0<=M_j<=1/4. Let
f_j(z)=(1/2+M_j z)^2(1+A_j z)^(-1/2). Direct differentiation gives

    f_j''(z)=2M_j^2/(1+A_j z)^(1/2)
      -2A_j M_j(1/2+M_j z)/(1+A_j z)^(3/2)
      +3A_j^2(1/2+M_j z)^2/[4(1+A_j z)^(5/2)].

On 0<=z<=1, the absolute values of these terms are bounded by
1/8, 3/8 and 27/64, respectively. Thus |f_j''|<=59/64. Taylor's theorem,
f_j(0)=1/4, f_j'(0)=M_j-A_j/8 and sum h_j=2 imply

    |C-1/2-tau^2 sum_j h_j(M_j-A_j/8)|<=59tau^4/64.

For q in interval j, let A(q)=(1+q^2)^2/16+q^2/2.
Since d'(q)=(q+2q^3)/8 has absolute value at most 3/8,
|M_j-eta-d(q)|<=3D/8. The alpha and beta differences above, with both
compared quantities bounded in absolute value by 1/2, give
|A_j-A(q)|<=D. Consequently replacing the weighted sum by the integral
costs at most D: the pointwise difference is at most D/2 over length 2.
Exact polynomial integration gives integral d=1/15 and integral A=17/30,
so integral(eta+d-A/8)=2eta-1/240. This proves (A).
All error constants are independent of n; no finite sector replay is needed.

## Concrete budget and controls

Choose tau=1/2000, eta=1/1000 and the uniform partition with n=1,000,000,
so D=1/500,000. Then

    G=247/2,000,000 >0,
    C <= 1/2 - 1662287/3072000000000000 <1/2.

The guaranteed saving is about 5.41109e-10. There are exactly 2,000,000
cylinders, with positive explicitly defined rational intercept cutoffs and axes.
This changes the source example's sector count, not its deformation mechanism.
The source's stated 2tau^4 remainder should NOT be reused at this coarser mesh;
(A) prices the larger mesh error explicitly. This is not an improvement over
Pinho's 4096-cylinder cover and saving greater than 0.000386.

At these tau,eta, the smallest uniform n allowed by (C) is 890125:
n=890124 gives negative G while n=890125 gives positive G. This is minimal
only for this sufficient budget, not a lower bound on possible covers.
The round count above is used for the displayed construction.

A genuine uncovered-point control uses tau=1/2, eta=0, nodes (-1,0,1),
and all cutoffs artificially set to 1/2. The point (x,y,t)=(1/10,3/10,21/40)
lies in K. Both selected positive-sector intercept heights equal 41/80>1/2;
their other intercept coordinates are positive, excluding the negative sectors.
Thus none of the four cylinders covers it. Restoring the defined enlargement
makes the selected cutoff 17/32 and covers the point. This is an actual failure
control, unlike merely evaluating G<0. The checker tests all four cylinders.
