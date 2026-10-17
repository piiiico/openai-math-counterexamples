# Explicit Gaussian parameters for the coarse report

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Written proof plus an exact rational certificate; not a formal proof or a
finite Boolean counterexample. The source reporting rule is credited below.

## Construction

Set

\[
m=2^{24}+1=16\,777\,217,\quad T=8,\quad c=3/8,\quad
h=2^{-20},\quad r=2^{-33}.
\]

There are `m+1 = 16,777,218` independent standard Gaussian inputs
`U,Z_1,...,Z_m`. Index the leaves by integers `-2^23 ≤ j ≤ 2^23`, and give
leaf `j` the interval `[c+jh-r,c+jh+r]`. For `|U|≤T`, select a nearest
grid point `jh`, breaking ties toward the smaller index. For `|U|>T`,
select `j=0`. These conventions cover the whole real line and both endpoints.

Let `B` be the event that all leaves pass their interval tests, `P` the
event that all unselected leaves pass, and `A=P\B`. Use the source's coarse
report: one mark on `A`, a different mark on `B`, and otherwise report `U`,
the selected index and every unselected leaf. Predict the input sum `L` by

- `b_0=(m-1)c=6,291,456` on `A`;
- `b_1=mc=6,291,456+3/8` on `B`;
- the sum of reported coordinates on `P^c`.

All parameters and predictor constants are rational. The observation on
Gaussian inputs is not finite-valued; it has finitely many parameters and
becomes finite-valued on any product of finite input alphabets.

**Claim.** If `Q` is the probability that every leaf passes, this predictor
has squared error less than `1-Q/50`. Consequently

\[
\operatorname{Var}(\mathbb E[L\mid\mathcal O])>m+Q/50,
\qquad Q>2^{-1\,426\,063\,445}.
\]

Every output indicator on finite alphabets is a linear combination of
functions of at most `m` input coordinates. No averaging copy counts,
amplification iteration counts, or Boolean readout are supplied here.

## Exact predictor identity

The predictor deficit on an event `E` means
`E[(1-(L-b)^2) 1_E]`, with the predictor `b` used on that event.

Write `β_i`, `μ_i`, `s_i²` for the probability, conditional mean and
variance of leaf interval `i`. Put `M=Σμ_i`, `S=Σs_i²`, and `δ=M-mc`.
Conditioning on `U=t` and the selected index `i`, the event `P` has
probability `Q/β_i`. The selected leaf remains unrestricted. Therefore,
with

\[
J_\delta=\int_{\mathbb R}
 \frac{(t+c+\delta-\mu_{i(t)})^2+S-s_{i(t)}^2}{\beta_{i(t)}}
 \phi(t)\,dt,
\]

the contribution of `P` to the predictor deficit using `b_0` is `-QJ_δ`.
On `B`, the deficit with `b_0` is `-Q(S+(δ+c)²)`, whereas the deficit
with `b_1` is `-Q(S+δ²)`. Subtracting the former from the `P`
contribution and adding the latter gives

\[
1-\mathbb E[(L-\widehat L)^2]=Q(c^2+2c\delta-J_\delta). \tag{1}
\]

Here ordinary reports contribute exactly `P(P^c)` to squared error: for
each selected index, that report and its event depend only on the central
input and unselected leaves; the omitted independent Gaussian has mean
zero and variance one. This accounts for every report, including both tails.
The mean of `L` is zero and its variance is `m+1`; conditional expectation
minimizes squared error, giving the claimed retained-variance implication.

This derives (1) directly. It uses the source's coarse report but does not
assume its asymptotic Gaussian or Boolean theorem.

## Uniform mean and variance bounds

Let `K=T+c+r`, `ε=h/2+r`, and `D=mKr²`. The certificate verifies
`exp(2Kr)<3`. For any interval centered at `a`, `|a|≤T+c`, the ratio
of its maximum to minimum Gaussian density is at most `exp(2Kr)`:
the derivative of `log φ(z)` is `-z`, of absolute value at most `K`.
By cancellation of the integral of `vφ(a)` on `[-r,r]` and the
mean-value bound `|φ(a+v)-φ(a)|≤|v| K sup φ`,

\[
|\mu-a|\le\frac{(2r^3/3)K\sup\phi}{2r\inf\phi}
 \le\frac{Kr^2}{3}e^{2Kr}<Kr^2.
\]

The grid is symmetric, so its interval centers sum to `mc`. Hence
`|δ|≤D`. Independently, the support bound gives `|μ-a|≤r` and
`s²≤E[(Z-a)² | interval]≤r²`, and therefore `S≤mr²`.

## Central and tail bounds

For `|t|≤T`, nearest-grid selection gives `|t-jh|≤h/2`. Every `z`
in the selected interval satisfies `z=t+c+e`, `|e|≤ε`. Thus

\[
\frac{\phi(t)}{\beta_{i(t)}}
 \le\frac1{2r}\exp\!\left(ct+\varepsilon|t|
                       +\frac{(c+\varepsilon)^2}{2}\right).
\]

The numerator of `J_δ` is at most `(ε+D)²+mr²`. Since `c>ε`,

\[
\int_{-T}^T e^{ct+\varepsilon|t|}\,dt
=\frac{e^{(c+\varepsilon)T}-1}{c+\varepsilon}
 +\frac{1-e^{-(c-\varepsilon)T}}{c-\varepsilon}
\le\frac{e^{(c+\varepsilon)T}}{c-\varepsilon}.
\]

It follows that

\[
J_{\rm central}\le
C_0:=\frac{(\varepsilon+D)^2+mr^2}{2r(c-\varepsilon)}
       \exp\!\left(\frac{(c+\varepsilon)^2}{2}
                        +(c+\varepsilon)T\right). \tag{2}
\]

On both tails, the selected interval is centered at `c` and has
probability at least `2rφ(c+r)`. The numerator is at most
`2t²+2(r+D)²+mr²`. Integration by parts and the Gaussian tail bound give

\[
\int_{|t|>T}\phi(t)\,dt\le2\phi(T)/T,\qquad
\int_{|t|>T}t^2\phi(t)\,dt\le2(T+1/T)\phi(T).
\]

Consequently

\[
J_{\rm tail}\le
C_1:=\frac{2(T+1/T)+(2(r+D)^2+mr^2)/T}{r}
       \exp\!\left(\frac{(c+r)^2-T^2}{2}\right). \tag{3}
\]

The sufficient inequality checked is therefore

\[
c^2-2cD-C_0-C_1>1/50. \tag{4}
\]

For every leaf interval, `|z|≤K`. Using `sqrt(2π)<3`,
`β_i ≥ 2rφ(K) > (2r/3)exp(-K²/2)`. The certificate verifies this
last quantity exceeds `2^-85`. Taking the product gives
`Q>2^(-85m)`, with `85m=1,426,063,445`. No underflow-prone product is
formed, and all `m` intervals are covered by the same proven bound.

## Rational exponential certificate

For rational `x≥0`, let `S_N(x)=Σ_{k=0}^N x^k/k!`. Positive terms give
`exp(x)≥S_N(x)`. If `x<N+2`, the subsequent ratios are at most
`x/(N+2)`, so

\[
e^x\le S_N(x)+\frac{x^{N+1}}{(N+1)!}\frac1{1-x/(N+2)}.
\]

The checker uses `N=128` and exact `Fraction` arithmetic. The central
bound uses an upper exponential enclosure. If `L≤exp(x)≤U`, the tail
upper bound uses `1/L`, whereas the interval-mass lower bound uses `1/U`.
Outward decimal displays are summaries; all acceptance decisions are rational.
The checker establishes these finite scalar inequalities. The written argument
above is the bridge to Gaussian conditional variance, not a kernel proof.

## Coordinate cost and limitations

The exceptional-cell identity is
`1_A = Σ_i 1_{selector(U)=i} Π_{j≠i} 1_{I_j}(Z_j) - Π_j 1_{I_j}(Z_j)`.
Every term uses at most `m` inputs. The `B` mark ignores `U`. An attained
ordinary report fixes `U` and `m-1` leaves; at least one of those leaves
fails, so the omitted leaf is unrestricted. Its indicator also uses only
`m` inputs. This holds pointwise, including endpoints, ties and unused labels.

The finite Gaussian construction has a huge dimension and an extremely small
certified gain. It is not an efficient Boolean construction, an optimal
schedule, or evidence that the full theorem has been formally verified.
Failure of (4) for a perturbed schedule only means this sufficient bound
failed; it does not establish that schedule has nonpositive actual gain.

## Source and credit

The reporting partition, coordinate-cost identity and amplification context
are from OpenAI's Family 192 manuscript, at commit
`1581d4cbdd69a0faf34b2089614fe2a814316a6a`,
`build/sections/02-reporting.tex` and `03-alternatives.tex` under
`preprints/Unbounded-Violations-of-the-Square-Root-Degree-Bound-September-26-2026`.
In particular, `03-alternatives.tex:47–58` permits arbitrary predictor constants
and states `Var(E[L | O]) ≥ m + E g`. The uniform dyadic schedule, rational
predictors and finite scalar certificate here make one such gain explicit.
Credit Pico/Håkon Åmdal's existing Family 192 census and small-Boolean search.
No claim of global novelty follows from our bounded overlap search.
