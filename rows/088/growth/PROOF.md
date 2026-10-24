# Sharp exponential growth in the simplex-product class

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written all-dimensions proof with exact algebra/finite comparisons, not a
kernel-checked proof or human peer review.

## Statement

Put c_d=(d+1)d^d/d! for integers d>=2. For n>=2 let M_n be the maximum of
product_i c_(d_i) over all partitions of n with every part d_i>=2, including
the one-part partition (n). Define a=c_13^(1/13), the positive root.

1. Every maximizing partition has all parts at most 19.
2. For every n>=2, M_n<=a^n. Equality holds exactly when 13 divides n;
   the only attaining unordered partition then consists entirely of 13s.
3. There is an explicit b>0 with b a^n<=M_n<=a^n for every n>=14. Hence

       lim_(n->infinity) M_n^(1/n)=a,
       lim_(n->infinity) (M_n/c_n)^(1/n)=a/e >1.

The source's product identity and simplex value identify these numbers with
the normalized projection-body volumes of Cartesian products of simplices.
A self-contained written geometric reduction is preserved in dependency/PROOF.md,
pinned to the accepted finite predecessor; its classical Cauchy/Fubini steps
are not kernel-verified. The arithmetic theorem above does not require a
geometric theorem as an assumption.

This is a restricted product class, with no one-dimensional factors. It is
not a universal upper bound over convex bodies, an all-dimensions exact
residue-class optimum formula, or a global novelty claim. The source gives a
fixed ten-dimensional factor exponential construction; the finite predecessor checks all
partitions through dimension 40. The new step is the analytic elimination of
all large factors, giving the sharp class-wide exponential rate.

## 1. Consecutive simplex ratios strictly decrease

The exact consecutive ratio is

    rho_n=c_(n+1)/c_n=((n+2)/(n+1))(1+1/n)^n.

Extend only this explicit expression to real x>=2 and let

    g(x)=log((x+2)/(x+1))+x log((x+1)/x).

Then

    g'(x)=log((x+1)/x)+1/(x+2)-2/(x+1).

Set t=1/(x+1), so 0<t<=1/3. For 0<t<1, elementary integration gives

    -log(1-t)=t+integral_0^t s/(1-s) ds
              < t+t^2/[2(1-t)].

The inequality is strict because for 0<s<t the integrand s/(1-s) is
strictly smaller than s/(1-t). Both denominators are positive; the difference
is exactly s(t-s)/[(1-t)(1-s)]. Therefore

    g'(x)<t+t^2/[2(1-t)]+t/(1+t)-2t
         =t^2(3t-1)/[2(1-t^2)] <=0.

The final denominator is positive and 3t-1<=0. This includes x=2:
the preceding strict integral bound makes g'(2)<0 even though the last
upper bound is zero. Thus rho_n is strictly decreasing for all integers n>=2.
No numerical derivative samples or gamma-function estimates are used.

## 2. Every factor of dimension at least 20 splits beneficially

For m>=2 let H_m=c_m^2/c_(2m). Exact factorial cancellation gives

    H_m=((m+1)^2/(2m+1)) binom(2m,m)/4^m,
    H_(m+1)/H_m=(m+2)^2(2m+1)^2/[2(2m+3)(m+1)^3].

The numerator minus denominator of the latter ratio is

    2m^3+3m^2-2m-2.

Writing m=u+1 turns this polynomial into

    2u^3+9u^2+10u+1 >0  for u>=0.

Hence H_m strictly increases for m>=2. The source's exact dimension-20
comparison, independently reproduced by integer arithmetic, is

    H_10=5588869/5505024>1.

Consequently c_m^2>c_(2m) for every m>=10. For odd dimensions,

    c_m c_(m+1)/c_(2m+1)=H_m rho_m/rho_(2m)>H_m>1

for m>=10, by strict decrease of rho. Thus every d>=20 has

    c_floor(d/2) c_ceil(d/2) > c_d.                    (S)

Both new factors have dimension at least ten and strictly less than d.
Replacing any large factor in a product therefore strictly increases its
value while preserving total dimension. Repeated replacement terminates:
the positive integer sum of squared part dimensions strictly decreases at
every split. A maximum exists because the number of partitions of a fixed
n is finite. No maximizing partition can contain a part at least 20.
The threshold cannot be strengthened to 19 by this argument: exact arithmetic
gives c_9 c_10<c_19. This is a genuine counterexample to that stronger split
claim, not merely failure of a numerical search.

## 3. Eighteen exact comparisons determine the density winner

For each d in {2,...,19}, compare c_13^d with c_d^13. Clearing positive
factorials leaves the integer difference

    [(14*13^13)^d (d!)^13]
      - [((d+1)d^d)^13 (13!)^d].                      (D)

The certificate recomputes all 18 differences. They are zero at d=13 and
strictly positive at all other d. These are complete finite checks of a
fixed set, not an extrapolation. Since all quantities are positive, taking
positive (13d)-th roots proves c_d^(1/d)<a for every d!=13 in that set.

Apply section 2 to any maximizing partition. Every remaining part is at most
19, and each factor c_d<=a^d, strictly unless d=13. Thus M_n<=a^n; equality
requires every part to be 13. Conversely, for n divisible by 13 that partition
is allowed and attains a^n. This proves both the upper bound and its equality
classification for every n>=2, including n<13.

## 4. Explicit residue construction and limiting rate

Write n=13k+r, 0<=r<=12. For n>=14 use:

- r=0: k factors of dimension 13;
- r=1: k-1 factors of dimension 13 and one factor of dimension 14;
- 2<=r<=12: k factors of dimension 13 and one factor of dimension r.

In the second case k>=1; no one-dimensional simplex is introduced. All counts
are nonnegative and all part dimensions are at least two. Define

    b_0=1, b_1=c_14/a^14, b_r=c_r/a^r (2<=r<=12),
    b=min_{0<=r<=12} b_r >0.

These products have value b_r a^n, proving the uniform lower bound b a^n.
The 13 constants are a fixed finite positive set; b does not depend on n.
Together with the upper bound this gives M_n^(1/n)->a.

For completeness, monotonicity of log on [1,n] gives

    n log n-n+1 <= log(n!) <= n log n-n+1+log n.

Since log c_n=log(n+1)+n log n-log(n!), it follows that
log c_n/n->1 and c_n^(1/n)->e. Taking the ratio of the two positive limits
proves the stated sharp excess rate a/e. The exact certificate also verifies
c_13>(11/4)^13. The exponential series gives e<11/4: its first three terms
sum to 5/2, and the tail from 1/3! is strictly less than
(1/6) sum_(j>=0)3^(-j)=1/4. Thus a/e>1 without decimal approximations.

## Verification boundaries

The checker verifies the finite integer comparisons, symbolic polynomial and
rational identities used above, and rigorous rational enclosures for a/e.
It checks residue constructions, including the residue-one repair. A finite
replay of splits or residue examples does not prove the universal statements;
the analytic arguments and integer decomposition above supply those proofs.
Separately tasked AI review is additional scrutiny, not human peer review.

The source's geometric mechanism, finite predecessor, and earlier convex-
geometry literature retain credit. The Math Referee panel's fixed ten-dimensional factor
quantitative corollary certificate is distinct from this optimized rate; its
review does not constitute review of the present extension.

For the numerical enclosure, let S_N=sum_(k=0)^N 1/k!. The positive tail
starts at 1/(N+1)! and subsequent ratios are at most 1/(N+1), strictly smaller
thereafter. Hence S_N<e<S_N+1/(N N!). The certificate uses N=20. Rational
endpoints L,U are checked directly by 0<L<U and L^13<=c_13<=U^13. Therefore
L/(S_20+1/(20*20!))<a/e<U/S_20. Exact cross multiplication verifies the
simpler display bounds 103/100 and 26/25. These finite enclosures do not prove
the limiting theorem; the earlier written arguments supply that proof.
