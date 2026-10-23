#!/usr/bin/env python3
"""Family 047: deterministic exact certificate for A[w] = k^[5] (standard library only).

Claim (openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb,
preprints/An-explicit-failure-of-complex-affine-space-cancellation-September-23-2026/
build/sections/01-introduction.tex:49-70, proof in 02-construction.tex:19-256):
with P = k[p,s,u,F,J], x = s^2+u^3+p^2F and H = x^2F-(1+2sx)J-p^2J^2-pu,
the algebra A = P/(H) satisfies A[w] = k^[5].

Every identity displayed in prop:stabilization, together with con:identity and the
H mod p identity of con:domain, is decided by full expansion in Z[p,s,u,F,J,M,L,w,E];
nothing is evaluated at random points. Beyond those displayed identities, the script
certifies the two steps the proof argues abstractly:

  * the exponential automorphism Phi = exp(w Delta): its images of the six generators,
    the inverse exp(-w Delta), both composites, and Phi(H) = H + p^3 w;
  * the isomorphism T = P[w]/(H + p^3 w) = Z[p,s,u,M,e]: both round trips, including an
    explicit quotient q with W(e0) - w = q (H + p^3 w).

All coefficients are integers, so the maps are defined over Z. Not computed: A is not
k^[4] (sections 03-06); the Laurent-ring identities and the irreducibility and dimension
arguments of con:domain; any statement about other papers. This is a finite
computation, not a kernel proof.

Usage: python3 check.py [--negative-control NAME]
"""
import argparse
import hashlib
import json
import sys
import time
from math import factorial

VARS = ("p", "s", "u", "F", "J", "M", "L", "w", "E")
INDEX = {name: i for i, name in enumerate(VARS)}
ZERO_EXP = (0,) * len(VARS)


class Poly:
    """Sparse polynomial with integer coefficients over VARS."""

    __slots__ = ("terms",)

    def __init__(self, terms=None):
        self.terms = {e: c for e, c in (terms or {}).items() if c}

    @classmethod
    def const(cls, c):
        return cls({ZERO_EXP: c})

    @classmethod
    def var(cls, name):
        e = [0] * len(VARS)
        e[INDEX[name]] = 1
        return cls({tuple(e): 1})

    @staticmethod
    def lift(other):
        if isinstance(other, Poly):
            return other
        if isinstance(other, int):
            return Poly.const(other)
        raise TypeError(f"cannot use {type(other).__name__} as a polynomial")

    def __add__(self, other):
        r = dict(self.terms)
        for e, c in Poly.lift(other).terms.items():
            r[e] = r.get(e, 0) + c
        return Poly(r)

    __radd__ = __add__

    def __neg__(self):
        return Poly({e: -c for e, c in self.terms.items()})

    def __sub__(self, other):
        return self + (-Poly.lift(other))

    def __rsub__(self, other):
        return Poly.lift(other) - self

    def __mul__(self, other):
        other = Poly.lift(other)
        r = {}
        for e1, c1 in self.terms.items():
            for e2, c2 in other.terms.items():
                e = tuple(a + b for a, b in zip(e1, e2))
                r[e] = r.get(e, 0) + c1 * c2
        return Poly(r)

    __rmul__ = __mul__

    def __pow__(self, n):
        r = Poly.const(1)
        for _ in range(n):
            r = r * self
        return r

    def __eq__(self, other):
        return (self - Poly.lift(other)).is_zero()

    __hash__ = None

    def is_zero(self):
        return not self.terms

    def __len__(self):
        return len(self.terms)

    def degree(self, name):
        i = INDEX[name]
        return max((e[i] for e in self.terms), default=-1)

    def uses_only(self, names):
        allowed = {INDEX[n] for n in names}
        return all(not k or i in allowed for e in self.terms for i, k in enumerate(e))

    def coeff(self, name, d):
        """Coefficient of name^d, as a polynomial free of name."""
        i = INDEX[name]
        return Poly({e[:i] + (0,) + e[i + 1:]: c for e, c in self.terms.items() if e[i] == d})

    def diff(self, name):
        i = INDEX[name]
        return Poly({e[:i] + (e[i] - 1,) + e[i + 1:]: c * e[i]
                     for e, c in self.terms.items() if e[i]})

    def divide_by_var_power(self, name, k):
        """Exact quotient by name^k, or None when some monomial is not divisible."""
        i = INDEX[name]
        if any(e[i] < k for e in self.terms):
            return None
        return Poly({e[:i] + (e[i] - k,) + e[i + 1:]: c for e, c in self.terms.items()})

    def divide_integer(self, d):
        """Exact quotient by the integer d, or None when some coefficient is not divisible."""
        if any(c % d for c in self.terms.values()):
            return None
        return Poly({e: c // d for e, c in self.terms.items()})

    def subst(self, values):
        """Simultaneous substitution {name: Poly}; other variables are kept."""
        idx = sorted(INDEX[n] for n in values)
        vals = {INDEX[n]: Poly.lift(v) for n, v in values.items()}
        groups = {}
        for e, c in self.terms.items():
            key = tuple(e[i] for i in idx)
            rest = list(e)
            for i in idx:
                rest[i] = 0
            g = groups.setdefault(key, {})
            g[tuple(rest)] = g.get(tuple(rest), 0) + c
        powers = {i: [Poly.const(1)] for i in idx}

        def power(i, k):
            cache = powers[i]
            while len(cache) <= k:
                cache.append(cache[-1] * vals[i])
            return cache[k]

        result = Poly()
        for key, rest in groups.items():
            factor = Poly(rest)
            for i, k in zip(idx, key):
                if k:
                    factor = factor * power(i, k)
            result = result + factor
        return result

    def canonical_sha256(self, order):
        """SHA-256 of the JSON list [[[exponents in `order`], coefficient], ...], sorted by
        exponents; independent/independent_check.py hashes the same serialization."""
        if not self.uses_only(order):
            raise ValueError("polynomial uses a variable outside the hash order")
        rows = sorted([[e[INDEX[n]] for n in order], c] for e, c in self.terms.items())
        return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()


p, s, u, F, J, M, L, w, E = (Poly.var(n) for n in VARS)
EXPECTED_CHECKS = 18  # a mutation that stops the sequence early must not pass
Q_HASH_ORDER = ("p", "s", "u", "M", "L", "w")
# q as computed by independent/independent_check.py (SymPy), same serialization.
EXPECTED_Q_SHA256 = "a74adf01ee2e0f13c37830a184051da1d706c85b6714704a15157443b4bc97f6"

# Each negative control changes one input of the construction; the check must then fail.
NEGATIVE_CONTROLS = {
    "H-coefficient": "H uses -2pu instead of -pu",
    "derivation-value": "Delta J = 3x^2u^2 + p instead of 3x^2u^2",
    "linear-coordinates": "M uses 5s^2 J instead of 4s^2 J (con:linear-coordinates)",
    "linear-inverse": "F(L,M) uses 5s^2 L instead of 4s^2 L (con:linear-inverse)",
    "e0-sign": "e0 = +w - pF^3 - Q1 h instead of -w - ...",
}


def build(control=None):
    """Objects of 02-construction.tex, optionally with one negative-control mutation."""
    o = {}
    o["x"] = x = s**2 + u**3 + p**2 * F
    o["y"] = s + x * (x - u**3)
    o["z"] = s * x + p**2 * J
    pu_coeff = 2 if control == "H-coefficient" else 1
    o["H"] = x**2 * F - (1 + 2 * s * x) * J - p**2 * J**2 - pu_coeff * p * u
    o["Delta"] = {                                    # con:derivation, and Delta w = 0
        "p": Poly(), "u": -p**2, "s": -3 * p**2 * x * u**2,
        "F": (6 * s * x + 3) * u**2,
        "J": 3 * x**2 * u**2 + (p if control == "derivation-value" else 0),
        "w": Poly(),
    }
    o["x0"] = x0 = s**2 + u**3
    m_coeff = 5 if control == "linear-coordinates" else 4
    f_coeff = 5 if control == "linear-inverse" else 4
    o["L_of_FJ"] = x0**2 * F - (1 + 2 * s * x0) * J          # con:linear-coordinates
    o["M_of_FJ"] = (1 - 2 * s * x0) * F + m_coeff * s**2 * J
    o["F_of_LM"] = FL = f_coeff * s**2 * L + (1 + 2 * s * x0) * M  # con:linear-inverse
    o["J_of_LM"] = JL = -(1 - 2 * s * x0) * L + x0**2 * M
    o["H_L"] = o["H"].subst({"F": FL, "J": JL})
    o["Q"] = Q = 2 * x0 * FL**2 - 2 * s * FL * JL - JL**2       # con:h-expansion
    o["C"] = C = Q.subst({"L": 0})
    o["C_formula"] = M**2 * (2 * x0 + 6 * s * x0**2 + 4 * s**2 * x0**3 - x0**4)
    o["Q1"] = (Q - C).divide_by_var_power("L", 1)
    o["L_star"] = p * u - p**2 * C
    o["h"] = u - p * Q - p**3 * FL**3 - p**2 * w                  # con:e-polynomial (h, e0)
    w_sign = 1 if control == "e0-sign" else -1
    Q1 = o["Q1"] if o["Q1"] is not None else Poly()
    o["e0"] = w_sign * w - p * FL**3 - Q1 * o["h"]
    return o


def apply_derivation(f, delta):
    return sum((f.diff(n) * v for n, v in delta.items()), Poly())


def exponential(delta, sign, generator, limit=64):
    """exp(sign * w * Delta)(generator), with exact division by i!, or None."""
    total, term = Poly(), generator
    for i in range(limit):
        if term.is_zero():
            return total
        scaled = term.divide_integer(factorial(i))
        if scaled is None:
            return None
        total = total + scaled * (sign * w) ** i
        term = apply_derivation(term, delta)
    return None


def exact_quotient_in_w(numerator, divisor):
    """Quotient q with numerator = q * divisor, dividing in w; divisor must be linear in w
    with leading coefficient p^3. Returns None otherwise, or when the division is not exact."""
    if divisor.degree("w") != 1 or not divisor.coeff("w", 1) == p**3:
        return None
    rest = divisor - p**3 * w
    quotient, remainder = Poly(), numerator
    while remainder.degree("w") >= 1:
        d = remainder.degree("w")
        c = remainder.coeff("w", d).divide_by_var_power("p", 3)
        if c is None:
            return None
        step = c * w ** (d - 1)
        quotient = quotient + step
        remainder = remainder - step * (p**3 * w + rest)
    return quotient if remainder.is_zero() else None


def run_checks(o):
    """Yield (label, ok, detail) for every certified identity."""
    x, y, z, H, delta = o["x"], o["y"], o["z"], o["H"], o["Delta"]

    yield ("con:identity  xy - z(z+1) = p^2(H + pu)",
           x * y - z * (z + 1) == p**2 * (H + p * u), "")

    yield ("con:localized-coordinates  s = y - x(x-u^3), p^2F = x-s^2-u^3, p^2J = z-sx",
           (y - x * (x - u**3)) == s and p**2 * F == x - s**2 - u**3 and p**2 * J == z - s * x,
           "holds by construction of x, y, z; recorded for completeness")

    x0 = o["x0"]
    yield ("con:domain  H mod p = x0^2 F - (1 + 2 s x0) J",
           H.subst({"p": 0}) == x0**2 * F - (1 + 2 * s * x0) * J, "")

    dx, dy, dz = (apply_derivation(f, delta) for f in (x, y, z))
    dH = apply_derivation(H, delta)
    yield ("con:derivation  Delta x = Delta y = Delta z = 0, Delta H = p^3, Delta^2 H = 0",
           dx.is_zero() and dy.is_zero() and dz.is_zero() and dH == p**3
           and apply_derivation(dH, delta).is_zero(), "")

    nil = {}
    for g in ("p", "s", "u", "F", "J"):
        term, k = Poly.var(g), 0
        while not term.is_zero() and k < 64:
            term, k = apply_derivation(term, delta), k + 1
        nil[g] = k if term.is_zero() else None
    yield ("local nilpotency  least k with Delta^k(g) = 0",
           all(v is not None for v in nil.values()),
           ", ".join(f"{g}:{k}" for g, k in nil.items()))

    gens = ("p", "s", "u", "F", "J", "w")
    phi = {g: exponential(delta, 1, Poly.var(g)) for g in gens}
    phi_inv = {g: exponential(delta, -1, Poly.var(g)) for g in gens}
    integral = all(v is not None for v in (*phi.values(), *phi_inv.values()))
    yield ("exp(+-w Delta) on generators: finite, with exact division by i! over Z", integral,
           "terms " + ", ".join(f"{g}:{len(phi[g])}" for g in gens) if integral else "")
    if not integral:
        return
    yield ("Phi(H) = H + p^3 w  (con:cylinder-automorphism)", H.subst(phi) == H + p**3 * w, "")
    yield ("Phi^-1(Phi(g)) = g = Phi(Phi^-1(g)) for g in p,s,u,F,J,w",
           all(phi[g].subst(phi_inv) == Poly.var(g) and phi_inv[g].subst(phi) == Poly.var(g)
               for g in gens), "")

    FL, JL, Lm, Mm = o["F_of_LM"], o["J_of_LM"], o["L_of_FJ"], o["M_of_FJ"]
    det = Lm.coeff("F", 1) * Mm.coeff("J", 1) - Lm.coeff("J", 1) * Mm.coeff("F", 1)
    yield ("con:linear-coordinates/-inverse  det = 1, both substitutions are identities",
           det == 1 and Lm.subst({"F": FL, "J": JL}) == L and Mm.subst({"F": FL, "J": JL}) == M
           and FL.subst({"L": Lm, "M": Mm}) == F and JL.subst({"L": Lm, "M": Mm}) == J, "")

    HL, Q, C = o["H_L"], o["Q"], o["C"]
    yield ("con:h-expansion  H(L) = L - pu + p^2 Q(L) + p^4 F(L)^3",
           HL == L - p * u + p**2 * Q + p**4 * FL**3, "")

    Q1 = o["Q1"]
    yield ("con:root  C = Q(0) = M^2(2x0+6sx0^2+4s^2x0^3-x0^4), L divides Q(L) - C",
           C == o["C_formula"] and Q1 is not None, "")
    if Q1 is None:
        return

    Ls = o["L_star"]
    yield ("con:root-divisibility  H(L*) = p^3((u - pC)Q1(L*) + pF(L*)^3)",
           HL.subst({"L": Ls}) == p**3 * ((u - p * C) * Q1.subst({"L": Ls})
                                          + p * FL.subst({"L": Ls})**3), "")

    D = HL + p**3 * w
    h, e0 = o["h"], o["e0"]
    yield ("H(L) + p^3 w = L - p h  (02-construction.tex:203)", D == L - p * h, "")
    yield ("con:e-certificate  p^3 e0 - (L - L*) = (p^2 Q1 - 1)(H(L) + p^3 w)",
           p**3 * e0 - (L - Ls) == (p**2 * Q1 - 1) * D, "")

    HZ = HL.subst({"L": Ls + p**3 * E})
    W_neg = HZ.divide_by_var_power("p", 3)
    yield ("p^3 divides H(L* + p^3 E) in B[E]; W(E) = -H(L* + p^3 E)/p^3",
           W_neg is not None, f"W terms {len(W_neg)}" if W_neg is not None else "")
    if W_neg is None:
        return
    W = -W_neg

    yield ("round trip Z[p,s,u,M,E] -> T -> Z[p,s,u,M,E]:  e0(L* + p^3 E, W(E)) = E",
           e0.subst({"L": Ls + p**3 * E, "w": W}) == E, "")

    R = W.subst({"E": e0}) - w
    q = exact_quotient_in_w(R, D)
    ok = q is not None and q * D == R
    yield ("round trip T -> Z[p,s,u,M,E] -> T:  W(e0) - w = q (H(L) + p^3 w), q explicit",
           ok, f"q terms {len(q)}" if ok else "")
    digest = q.canonical_sha256(Q_HASH_ORDER) if ok else None
    yield ("q equals the independently computed quotient (canonical SHA-256)",
           digest == EXPECTED_Q_SHA256, f"sha256 {digest}" if ok else "")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--negative-control", choices=sorted(NEGATIVE_CONTROLS))
    args = parser.parse_args(argv)
    start = time.time()
    if args.negative_control:
        print(f"NEGATIVE CONTROL {args.negative_control}: {NEGATIVE_CONTROLS[args.negative_control]}")
    results = list(run_checks(build(args.negative_control)))
    for label, ok, detail in results:
        print(f"{'ok  ' if ok else 'FAIL'} {label}" + (f"  [{detail}]" if detail else ""))
    holds = len(results) == EXPECTED_CHECKS and all(ok for _, ok, _ in results)
    print(f"{len(results)} checks")
    print(f"runtime {time.time() - start:.1f}s", file=sys.stderr)
    if holds:
        print("RESULT: holds -- exact Z-polynomial certificate: Phi gives A[w] = P[w]/(H + p^3 w) = T, "
              "and T = Z[p,s,u,M,e] by explicit mutually inverse maps")
    else:
        print("RESULT: fails")
    return 0 if holds else 1


if __name__ == "__main__":
    sys.exit(main())
