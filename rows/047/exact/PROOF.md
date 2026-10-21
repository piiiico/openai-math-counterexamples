# From the computed identities to A[w] ≅ k^[5]

This note derives the stabilization half of the main theorem from the identities
that `check.py` verifies by full expansion. It follows the manuscript's own
construction (02-construction.tex:97-256) and makes explicit two steps that the
manuscript argues abstractly. All objects are those of the manuscript. Its base
field is k = ℂ (`\kk` is defined in preamble.tex:24, copied to `source/`).

Let R be any commutative ring. Every polynomial below has integer coefficients,
so each identity checked in ℤ[p,s,u,F,J,M,L,w,E] also holds over R. Put
P_R = R[p,s,u,F,J], H as in the manuscript, A_R = P_R/(H), and
T_R = P_R[w]/(H + p³w). Because adjoining a variable commutes with taking a
quotient, A_R[w] = P_R[w]/(H).

**Step 1: the exponential automorphism.** Define ring endomorphisms Φ and Φ'
of P_R[w] by their values on the six generators: Φ(g) = Σᵢ wⁱΔⁱ(g)/i! and
Φ'(g) = Σᵢ (−w)ⁱΔⁱ(g)/i!, where Δ takes the values of con:derivation and
Δw = 0. The check computes these finite sums and confirms that every division
by i! is exact over ℤ. It also verifies Φ'(Φ(g)) = g and Φ(Φ'(g)) = g for
g = p,s,u,F,J,w. An endomorphism of a polynomial ring is determined by its
values on generators, so Φ'∘Φ and Φ∘Φ' are the identity. Hence Φ is an
automorphism. The check verifies Φ(H) = H + p³w, so Φ maps the ideal (H) onto
(H + p³w) and induces A_R[w] ≅ T_R.

This step uses neither local nilpotency nor the exponential identity: the
computed inverse replaces them. The check still reports the nilpotency indices
(Δ⁴s = Δ⁷F = Δ⁴J = 0) as a consistency check.

**Step 2: new coordinates.** The substitutions (F,J) ↦ (F(L,M), J(L,M)) of
con:linear-inverse and (L,M) ↦ (L(F,J), M(F,J)) of con:linear-coordinates are
verified to be mutually inverse. So P_R[w] = B_R[L,w] with B_R = R[p,s,u,M], and
H becomes H(L). Thus T_R = B_R[L,w]/(D), where D = H(L) + p³w.

**Step 3: a map T_R → B_R[E].** The check verifies that H(L* + p³E) is divisible
by p³ in ℤ[p,s,u,M,E], and defines W(E) = −H(L* + p³E)/p³. The B_R-algebra map
φ̃: B_R[L,w] → B_R[E] given by L ↦ L* + p³E and w ↦ W(E) sends D to
H(L* + p³E) + p³W(E) = 0. It therefore factors through a map φ: T_R → B_R[E].

**Step 4: a map B_R[E] → T_R.** Let ψ be the B_R-algebra map with E ↦ e (the
class of e₀). It is defined because B_R[E] is a polynomial ring.

**Step 5: φ∘ψ = id.** Both maps fix B_R. On E, φ(ψ(E)) = e₀(L* + p³E, W(E)),
which the check verifies is identically E.

**Step 6: ψ∘φ = id.** Both maps fix B_R. On L, ψ(φ(L)) = L* + p³e₀. By
con:e-certificate, (L* + p³e₀) − L = (p²Q₁ − 1)·D, which is 0 in T_R. On w,
ψ(φ(w)) = W(e₀). The check computes an explicit q ∈ ℤ[p,s,u,M,L,w] (6,641 terms;
canonical SHA-256 printed in `output.txt`) and verifies W(e₀) − w = q·D by
expansion. So W(e₀) = w in T_R. The two maps agree with the identity on the
generators B_R, L, w, so ψ∘φ is the identity.

**Conclusion.** T_R ≅ B_R[E] = R[p,s,u,M,E] ≅ R^[5]. Together with Step 1,
A_R[w] ≅ R^[5] for every commutative ring R; taking R = ℂ gives the
manuscript's stabilization statement. The isomorphism sends the classes of
Φ'(p), Φ'(s), Φ'(u), Φ'(M), Φ'(e₀) to the five variables, as the manuscript
states at 02-construction.tex:246-255.

The argument does not use that A or T is a domain, nor that p is a nonzero
element of T. The manuscript needs both to cancel p³ (02-construction.tex:239-241);
here the explicit quotient q replaces that step.

## Scope

- **Established:** a written derivation from exact finite computations. It is
  not a kernel-checked proof. The manuscript's argument is credited. The
  observation that the maps are defined over ℤ follows directly from its
  formulas; no novelty is claimed for it.
- **Not considered:** A_R ≇ R^[4] (manuscript sections 03–06), for ℂ or for any
  other ring. The cancellation counterexample needs that half, so this note
  says nothing about cancellation over rings other than ℂ.
- **Used by the chain:** the *definitions* of Q (con:h-expansion), C = Q(0)
  and L* (con:root), and h and e₀ (con:e-polynomial). The chain also uses the
  identities checked in Steps 1–6.
- **Verified but not used by the chain:** these displayed identities:
  - con:identity;
  - con:localized-coordinates (which holds by construction);
  - H mod p from con:domain;
  - the Δ-annihilation identities;
  - H(L) = L − pu + p²Q(L) + p⁴F(L)³ (con:h-expansion);
  - the displayed formula for C;
  - con:root-divisibility;
  - H(L) + p³w = L − ph (line 203).

  They are verified because the manuscript's own argument relies on them. The
  Laurent-ring identities (con:localized-h and the formula for u) are not
  checked by `check.py`; the independent implementation checks them in
  ℤ[p,t,x,y,z,u]/(pt − 1).
