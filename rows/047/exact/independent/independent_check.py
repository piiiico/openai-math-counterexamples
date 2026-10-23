#!/usr/bin/env python3
"""Independent exact verification of the explicit polynomial cylinder A[w] = C^[5].

Source
------
openai/math commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb,
``preprints/An-explicit-failure-of-complex-affine-space-cancellation-September-23-2026/build/sections/02-construction.tex``
(Proposition ``prop:stabilization``), together with the setup of
``01-introduction.tex`` (Theorem ``thm:main``).

Claim checked
-------------
Let ``P = C[p,s,u,F,J]``, ``x = s^2 + u^3 + p^2 F`` and

    H = x^2 F - (1 + 2 s x) J - p^2 J^2 - p u,        A = P/(H).

Proposition prop:stabilization: "For the algebra A in con:setup, there is an
algebraic C-isomorphism A[w] = C^[5]."  The manuscript proves this by an
explicit route: the locally nilpotent derivation Delta of con:derivation, the
exponential automorphism Phi = exp(w Delta) with Phi(H) = H + p^3 w, the linear
change (F, J) -> (L, M) of con:linear-coordinates, the root L_* modulo p^3
(con:root), and the fifth coordinate e_0 (con:e-polynomial,
con:e-certificate), giving T = P[w]/(H + p^3 w) = Z[p,s,u,M,e] after the
polynomial W(Z) = -H(L_* + p^3 Z)/p^3 recovers w.

This script re-derives every identity on that route by full expansion of
polynomials with integer coefficients (SymPy sparse ``ring`` over ``ZZ``).
Nothing is sampled or evaluated at random points.  Integer identities imply
the same identities over C.

Provenance
----------
The author was given two inputs: the manuscript sources ``01-introduction.tex``
and ``02-construction.tex``, and a task specification.  The specification
listed the checks to perform (the numbered steps below), the negative-control
names and their mutations, and the serialization used to hash q in check 13.
The author did not see the packet's other implementation (``check.py``) or its
tests.  The formulas themselves were transcribed from the manuscript.

Representation choices
----------------------
* ``P[w] = Z[p,s,u,F,J,w]``; ``B[L,w] = Z[p,s,u,M,L,w]`` with ``B = Z[p,s,u,M]``;
  ``B[Z] = Z[p,s,u,M,Z]``.
* The localization ``Z[p,p^-1,x,y,z,u]`` is ``Z[p,t,x,y,z,u]/(pt - 1)``; the
  normal form cancels ``min(e_p, e_t)`` from every monomial.
* A ring map is given by the images of the generators; ``substitute`` applies it
  exactly.  Phi and Phi^-1 on a non-generator are computed this way and, for H,
  also by the exponential series, as a cross-check of the homomorphism property.
* The polynomial q of check 13 is serialized as the JSON array
  ``[[[e_p,e_s,e_u,e_M,e_L,e_w],c], ...]`` sorted ascending by exponent tuple,
  written with ``separators=(",", ":")``, UTF-8 encoded, then hashed with SHA-256.

Usage
-----
    uv run --no-project --with sympy==1.14.0 python3 independent/independent_check.py
    ... --negative-control {H-coefficient,derivation-value,linear-coordinates,linear-inverse,e0-sign}

Prints one line per check and ends with ``RESULT: holds`` (exit 0) or
``RESULT: fails`` (exit 1).  ``holds`` requires every check to pass and exactly
``EXPECTED_RESULTS`` results, so dropping a step cannot pass silently.  No
``assert`` statements are used, so ``python -O`` rejects identically.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import sys
import time
from types import SimpleNamespace
from typing import Callable, Optional, Sequence

import sympy
from sympy.external.gmpy import GROUND_TYPES
from sympy.polys.domains import ZZ
from sympy.polys.rings import PolyElement, PolyRing, ring

NILPOTENCY_CAP = 64  # give up (and fail) if Delta^k(g) is still nonzero at k = cap
EXPECTED_RESULTS = 25  # result lines a full run must produce; any other count fails


# --------------------------------------------------------------------------
# Manuscript constants that the negative controls perturb.
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class Manuscript:
    """Integer constants read off the manuscript.  Defaults are the manuscript's."""

    h_pu_coefficient: int = -1  # H = ... - p u                      (con:setup)
    delta_J_p_shift: int = 0  # Delta J = 3 x^2 u^2 (+ shift * p)    (con:derivation)
    m_s2_coefficient: int = 4  # M = (1 - 2 s x0) F + 4 s^2 J        (con:linear-coordinates)
    f_s2L_coefficient: int = 4  # F = 4 s^2 L + (1 + 2 s x0) M        (con:linear-inverse)
    e0_w_coefficient: int = -1  # e0 = -w - p F^3 - Q1 h              (con:e-polynomial)


NEGATIVE_CONTROLS: dict[str, dict[str, int]] = {
    "H-coefficient": {"h_pu_coefficient": -2},
    "derivation-value": {"delta_J_p_shift": 1},
    "linear-coordinates": {"m_s2_coefficient": 5},
    "linear-inverse": {"f_s2L_coefficient": 5},
    "e0-sign": {"e0_w_coefficient": +1},
}


# --------------------------------------------------------------------------
# Manuscript formulas, written once and evaluated in whichever ring is needed.
# --------------------------------------------------------------------------


def x_of(p, s, u, F):
    return s**2 + u**3 + p**2 * F


def y_of(s, u, x):
    return s + x * (x - u**3)


def z_of(p, s, x, J):
    return s * x + p**2 * J


def H_of(p, s, u, F, J, ms: Manuscript):
    x = x_of(p, s, u, F)
    return x**2 * F - (1 + 2 * s * x) * J - p**2 * J**2 + ms.h_pu_coefficient * p * u


def derivation_values(p, s, u, F, J, ms: Manuscript):
    """con:derivation, in the generator order (p, s, u, F, J)."""
    x = x_of(p, s, u, F)
    zero = p - p
    return (
        zero,  # Delta p
        -3 * p**2 * x * u**2,  # Delta s
        -(p**2),  # Delta u
        (6 * s * x + 3) * u**2,  # Delta F
        3 * x**2 * u**2 + ms.delta_J_p_shift * p,  # Delta J
    )


def linear_coordinates(s, u, F, J, ms: Manuscript):
    """con:linear-coordinates: (F, J) -> (L, M)."""
    x0 = s**2 + u**3
    L = x0**2 * F - (1 + 2 * s * x0) * J
    M = (1 - 2 * s * x0) * F + ms.m_s2_coefficient * s**2 * J
    return L, M


def linear_inverse(s, u, L, M, ms: Manuscript):
    """con:linear-inverse: (L, M) -> (F, J)."""
    x0 = s**2 + u**3
    F = ms.f_s2L_coefficient * s**2 * L + (1 + 2 * s * x0) * M
    J = -(1 - 2 * s * x0) * L + x0**2 * M
    return F, J


def Q_of(s, u, F, J):
    """Q in con:h-expansion."""
    x0 = s**2 + u**3
    return 2 * x0 * F**2 - 2 * s * F * J - J**2


def C_displayed(s, u, M):
    """The displayed closed form of C = Q(0) in con:root."""
    x0 = s**2 + u**3
    return M**2 * (2 * x0 + 6 * s * x0**2 + 4 * s**2 * x0**3 - x0**4)


# --------------------------------------------------------------------------
# Exact polynomial utilities.
# --------------------------------------------------------------------------


def bare_generator_index(f: PolyElement) -> Optional[int]:
    """Index j if f is exactly the j-th generator of its ring, else None."""
    if len(f) != 1:
        return None
    ((monom, coeff),) = f.items()
    if coeff != 1 or sum(monom) != 1:
        return None
    return monom.index(1)


def substitute(f: PolyElement, target: PolyRing, images: Sequence[Optional[PolyElement]]) -> PolyElement:
    """Image of f under the ring map sending source generator i to images[i].

    ``images[i] is None`` declares that generator i must not occur in f (a
    ValueError is raised if it does).  Generators mapped to bare target
    generators are renamed directly; the others are expanded with cached
    powers, grouped by their exponent pattern.
    """
    src = f.ring
    if len(images) != src.ngens:
        raise ValueError("need one image per source generator")
    simple: dict[int, int] = {}
    compound: list[int] = []
    for i, img in enumerate(images):
        if img is None:
            continue
        if img.ring != target:
            raise ValueError(f"image of {src.symbols[i]} is not in the target ring")
        j = bare_generator_index(img)
        if j is None:
            compound.append(i)
        else:
            simple[i] = j
    compound_set = set(compound)

    buckets: dict[tuple, dict[tuple, int]] = {}
    for monom, coeff in f.items():
        tm = [0] * target.ngens
        for i, e in enumerate(monom):
            if not e:
                continue
            if i in simple:
                tm[simple[i]] += e
            elif i not in compound_set:
                raise ValueError(f"generator {src.symbols[i]} occurs but has no image")
        key = tuple(monom[i] for i in compound)
        bucket = buckets.setdefault(key, {})
        tmt = tuple(tm)
        bucket[tmt] = bucket.get(tmt, 0) + coeff

    powers = {i: [target.one] for i in compound}

    def power(i: int, n: int) -> PolyElement:
        cache = powers[i]
        while len(cache) <= n:
            cache.append(cache[-1] * images[i])
        return cache[n]

    acc: dict[tuple, int] = {}
    for key, bucket in buckets.items():
        term = target.from_dict({m: c for m, c in bucket.items() if c})
        for i, n in zip(compound, key):
            if n:
                term = term * power(i, n)
        for m, c in term.items():
            acc[m] = acc.get(m, 0) + c
    return target.from_dict({m: c for m, c in acc.items() if c})


def divide_by_term(f: PolyElement, monom: Sequence[int], coeff: int = 1) -> Optional[PolyElement]:
    """f / (coeff * X^monom) if the division is exact in Z[gens], else None."""
    out: dict[tuple, int] = {}
    for m, c in f.items():
        if any(a < b for a, b in zip(m, monom)) or c % coeff:
            return None
        out[tuple(a - b for a, b in zip(m, monom))] = c // coeff
    return f.ring.from_dict(out)


def divide_by_gen_power(f: PolyElement, gen: PolyElement, k: int) -> Optional[PolyElement]:
    R = f.ring
    monom = [0] * R.ngens
    monom[R.index(gen)] = k
    return divide_by_term(f, monom)


def divide_by_integer(f: PolyElement, n: int) -> Optional[PolyElement]:
    return divide_by_term(f, f.ring.zero_monom, n)


def coefficients_in(f: PolyElement, gen: PolyElement) -> dict[int, PolyElement]:
    """{k: f_k} with f = sum_k f_k gen^k and every f_k free of gen."""
    R = f.ring
    i = R.index(gen)
    parts: dict[int, dict[tuple, int]] = {}
    for m, c in f.items():
        mm = list(m)
        k, mm[i] = mm[i], 0
        parts.setdefault(k, {})[tuple(mm)] = c
    return {k: R.from_dict(d) for k, d in parts.items()}


def divide_linear_in(D: PolyElement, G: PolyElement, gen: PolyElement) -> tuple[Optional[PolyElement], str]:
    """Exact quotient q with D = q G, where G = g1*gen + g0 and g1 is a single term.

    Division is carried out in (Z[other gens])[gen].  Every step divides by the
    single term g1, which must be exact, and the final remainder must vanish.
    Returns (q, "") or (None, reason).
    """
    R = D.ring
    Gc = coefficients_in(G, gen)
    if set(Gc) - {0, 1} or 1 not in Gc or len(Gc[1]) != 1:
        return None, "divisor is not linear in the variable with a single-term leading coefficient"
    g0 = Gc.get(0, R.zero)
    ((g1_monom, g1_coeff),) = Gc[1].items()
    Dc = coefficients_in(D, gen)
    n = max(Dc) if Dc else 0
    if n == 0:
        rem = Dc.get(0, R.zero)
        return (R.zero, "") if not rem else (None, "nonzero remainder in degree 0")
    q: dict[int, PolyElement] = {}
    carry = Dc.get(n, R.zero)
    for k in range(n, 0, -1):
        qk = divide_by_term(carry, g1_monom, g1_coeff)
        if qk is None:
            return None, f"inexact division by the leading coefficient at {gen}^{k}"
        q[k - 1] = qk
        carry = Dc.get(k - 1, R.zero) - g0 * qk
    if carry:
        return None, f"nonzero remainder with {len(carry)} terms"
    return sum((qk * gen**k for k, qk in q.items()), R.zero), ""


def laurent_normal_form(f: PolyElement, i_pos: int, i_neg: int) -> PolyElement:
    """Normal form in R/(X_pos X_neg - 1): cancel min(e_pos, e_neg) per monomial."""
    acc: dict[tuple, int] = {}
    for m, c in f.items():
        mm = list(m)
        k = min(mm[i_pos], mm[i_neg])
        mm[i_pos] -= k
        mm[i_neg] -= k
        t = tuple(mm)
        acc[t] = acc.get(t, 0) + c
    return f.ring.from_dict({m: c for m, c in acc.items() if c})


def canonical_json(f: PolyElement) -> str:
    return json.dumps([[list(m), int(c)] for m, c in sorted(f.items())], separators=(",", ":"))


# --------------------------------------------------------------------------
# Reporting.
# --------------------------------------------------------------------------


class Skip(Exception):
    """A prerequisite of this check failed, so the check could not be run."""


class Report:
    def __init__(self) -> None:
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def record(self, label: str, ok: bool, detail: str = "") -> bool:
        if ok:
            self.passed += 1
        else:
            self.failed += 1
        print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ""), flush=True)
        return ok

    def skip(self, label: str, reason: str) -> None:
        self.skipped += 1
        print(f"[SKIP] {label}: {reason}", flush=True)

    @property
    def total(self) -> int:
        return self.passed + self.failed + self.skipped

    @property
    def holds(self) -> bool:
        return self.failed == 0 and self.skipped == 0 and self.passed == EXPECTED_RESULTS


def need(ctx: SimpleNamespace, *names: str) -> None:
    missing = [n for n in names if getattr(ctx, n, None) is None]
    if missing:
        raise Skip("prerequisite unavailable: " + ", ".join(missing))


STEPS: list[tuple[str, Callable[[SimpleNamespace, Report], None]]] = []


def step(label: str):
    def register(fn):
        STEPS.append((label, fn))
        return fn

    return register


# --------------------------------------------------------------------------
# The checks, in the order of the manuscript's argument.
# --------------------------------------------------------------------------


@step("01 con:identity")
def check_identity(ctx, rep):
    p, s, u, F, J, w = ctx.RP.gens
    ms = ctx.ms
    x = x_of(p, s, u, F)
    y = y_of(s, u, x)
    z = z_of(p, s, x, J)
    H = H_of(p, s, u, F, J, ms)
    ctx.x, ctx.y, ctx.z, ctx.H = x, y, z, H
    lhs = x * y - z * (z + 1)
    rep.record(
        "01 con:identity",
        lhs == p**2 * (H + p * u),
        f"xy - z(z+1) = p^2(H + pu) in Z[p,s,u,F,J] ({len(lhs)} terms; H has {len(H)} terms)",
    )


@step("02 con:localized-coordinates")
def check_localized(ctx, rep):
    need(ctx, "x", "y", "z", "H")
    p, s, u, F, J, w = ctx.RP.gens
    x, y, z = ctx.x, ctx.y, ctx.z

    # (a) P -> localized -> P, clearing p^-2 by exact division in P.
    s_back = y - x * (x - u**3)
    F_back = divide_by_gen_power(x - s_back**2 - u**3, p, 2)
    J_back = divide_by_gen_power(z - s_back * x, p, 2)
    ok_a = s_back == s and F_back is not None and F_back == F and J_back is not None and J_back == J
    rep.record(
        "02a con:localized-coordinates (P -> localized -> P)",
        ok_a,
        "y - x(x-u^3) = s; x - s^2 - u^3 = p^2 F; z - sx = p^2 J (exact division by p^2)",
    )

    # (b) localized -> P -> localized, in Z[p,t,x,y,z,u]/(pt-1).
    RL = ctx.RL
    lp, lt, lx, ly, lz, lu = RL.gens
    lnf = ctx.lnf
    sL = ly - lx * (lx - lu**3)
    FL = lt**2 * (lx - sL**2 - lu**3)
    JL = lt**2 * (lz - sL * lx)
    ctx.loc = (lp, sL, lu, FL, JL)  # images of (p, s, u, F, J) in the localization
    xL = x_of(lp, sL, lu, FL)
    yL = y_of(sL, lu, xL)
    zL = z_of(lp, sL, xL, JL)
    ok_b = lnf(xL) == lx and lnf(yL) == ly and lnf(zL) == lz
    rep.record(
        "02b con:localized-coordinates (localized -> P -> localized)",
        ok_b,
        "with s = y - x(x-u^3), F = p^-2(x - s^2 - u^3), J = p^-2(z - sx): x, y, z are returned",
    )

    # (c) con:localized-h, as an identity of Laurent polynomials.
    HL = H_of(lp, sL, lu, FL, JL, ctx.ms)
    ctx.H_loc = lnf(HL)
    rhs = lt**2 * (lx * ly - lz * (lz + 1)) - lp * lu
    rep.record(
        "02c con:localized-h",
        ctx.H_loc == lnf(rhs),
        f"H = p^-2(xy - z(z+1)) - pu in Z[p,p^-1,x,y,z,u] ({len(ctx.H_loc)} terms)",
    )

    # (d) lemma con:domain: u = p^-3(xy - z(z+1)) modulo H, and H mod p.
    resid = lnf(lu - lt**3 * (lx * ly - lz * (lz + 1)) + lt * HL)
    x0 = s**2 + u**3
    H_mod_p = substitute(ctx.H, ctx.RP, [ctx.RP.zero, s, u, F, J, w])
    ok_d = not resid and H_mod_p == x0**2 * F - (1 + 2 * s * x0) * J
    rep.record(
        "02d con:domain (extra)",
        ok_d,
        "u - p^-3(xy - z(z+1)) = -p^-1 H; H mod p = x0^2 F - (1 + 2 s x0) J",
    )


@step("03 con:derivation")
def check_derivation(ctx, rep):
    need(ctx, "x", "y", "z", "H", "loc", "H_loc")
    RP = ctx.RP
    p, s, u, F, J, w = RP.gens
    values = list(derivation_values(p, s, u, F, J, ctx.ms)) + [RP.zero]  # Delta w = 0

    def Delta(f: PolyElement) -> PolyElement:
        return sum((f.diff(g) * v for g, v in zip(RP.gens, values) if v), RP.zero)

    ctx.Delta = Delta

    # (a) The displayed values are what -p^2 d/du gives on con:localized-coordinates.
    lnf = ctx.lnf
    lp, lt, lx, ly, lz, lu = ctx.RL.gens
    loc_values = derivation_values(*ctx.loc, ctx.ms)
    mismatches = [
        name
        for name, g, v in zip("psuFJ", ctx.loc, loc_values)
        if lnf(-(lp**2) * g.diff(lu)) != lnf(v)
    ]
    rep.record(
        "03a con:derivation values = -p^2 d/du of con:localized-coordinates",
        not mismatches,
        "Delta p=0, Delta u=-p^2, Delta s=-3p^2xu^2, Delta F=(6sx+3)u^2, Delta J=3x^2u^2"
        + (f"; mismatch at {','.join(mismatches)}" if mismatches else ""),
    )

    # (b) x, y, z are constants of Delta.
    dx, dy, dz = Delta(ctx.x), Delta(ctx.y), Delta(ctx.z)
    rep.record(
        "03b Delta x = Delta y = Delta z = 0",
        not dx and not dy and not dz,
        f"term counts of Delta x, Delta y, Delta z: {len(dx)}, {len(dy)}, {len(dz)}",
    )

    # (c) Delta H = p^3, Delta^2 H = 0.
    dH = Delta(ctx.H)
    ddH = Delta(dH)
    rep.record("03c Delta H = p^3 and Delta^2 H = 0", dH == p**3 and not ddH, f"Delta H has {len(dH)} terms")

    # (d) Local nilpotency on generators; the index must equal deg_u(localized form) + 1.
    indices: dict[str, int] = {}
    iterates: dict[str, list[PolyElement]] = {}
    ok_d = True
    notes = []
    for name, g, gl in zip(("p", "s", "u", "F", "J", "w"), RP.gens, list(ctx.loc) + [None]):
        seq = [g]
        while seq[-1] and len(seq) <= NILPOTENCY_CAP:
            seq.append(Delta(seq[-1]))
        if seq[-1]:
            ok_d = False
            notes.append(f"{name}: not nilpotent within {NILPOTENCY_CAP}")
            continue
        k = len(seq) - 1  # least k with Delta^k(g) = 0
        indices[name] = k
        iterates[name] = seq[:-1]  # Delta^0 .. Delta^{k-1}
        if gl is not None:
            expected = lnf(gl).degree(lu) + 1
            if k != expected:
                ok_d = False
                notes.append(f"{name}: k={k} but deg_u(localized)+1={expected}")
        elif k != 1:
            ok_d = False
            notes.append(f"{name}: k={k}, expected 1")
    ctx.iterates = iterates if ok_d else None
    rep.record(
        "03d Delta locally nilpotent on generators (least k with Delta^k g = 0)",
        ok_d,
        " ".join(f"{n}:{k}" for n, k in indices.items())
        + " (each equals deg_u in localized coordinates + 1)"
        + ("; " + "; ".join(notes) if notes else ""),
    )


@step("04 exponential automorphism Phi = exp(w Delta)")
def check_exponential(ctx, rep):
    need(ctx, "Delta", "iterates", "H")
    RP = ctx.RP
    p, s, u, F, J, w = RP.gens
    names = ("p", "s", "u", "F", "J", "w")

    def exp_images(sign: int):
        images, inexact = [], []
        for name in names:
            total = RP.zero
            for i, d in enumerate(ctx.iterates[name]):
                q = divide_by_integer(d, math.factorial(i))
                if q is None:
                    inexact.append(f"{name}@i={i}")
                    q = RP.zero
                total += (sign * w) ** i * q
            images.append(total)
        return images, inexact

    Phi, inexact_f = exp_images(+1)
    Phi_inv, inexact_b = exp_images(-1)
    rep.record(
        "04a Delta^i(g)/i! exact over ZZ for all generators",
        not inexact_f and not inexact_b,
        "max i per generator: "
        + " ".join(f"{n}:{len(ctx.iterates[n]) - 1}" for n in names)
        + "; Phi term counts: "
        + " ".join(f"{n}:{len(f)}" for n, f in zip(names, Phi))
        + ("; inexact at " + ",".join(inexact_f + inexact_b) if inexact_f or inexact_b else ""),
    )

    target = ctx.H + p**3 * w
    Phi_H_subst = substitute(ctx.H, RP, Phi)
    Phi_H_series: Optional[PolyElement] = RP.zero
    d, i = ctx.H, 0
    while d and i <= NILPOTENCY_CAP:
        q = divide_by_integer(d, math.factorial(i))
        if q is None:
            Phi_H_series = None
            break
        Phi_H_series += w**i * q
        d, i = ctx.Delta(d), i + 1
    series_ok = Phi_H_series is not None and not d and Phi_H_series == target
    rep.record(
        "04b Phi(H) = H + p^3 w",
        Phi_H_subst == target and series_ok,
        "H at the Phi-images of p,s,u,F,J equals H + p^3 w; the series exp(w Delta)(H) agrees",
    )

    bad = []
    for name, g, a, b in zip(names, RP.gens, Phi, Phi_inv):
        if substitute(b, RP, Phi) != g:
            bad.append(f"Phi(Phi^-1({name}))")
        if substitute(a, RP, Phi_inv) != g:
            bad.append(f"Phi^-1(Phi({name}))")
    rep.record(
        "04c Phi o Phi^-1 = Phi^-1 o Phi = id on p,s,u,F,J,w",
        not bad,
        "Phi^-1 = exp(-w Delta); both composites computed by substitution"
        + ("; failing: " + ", ".join(bad) if bad else ""),
    )


@step("05 con:linear-coordinates / con:linear-inverse")
def check_linear_change(ctx, rep):
    RP, RT, ms = ctx.RP, ctx.RT, ctx.ms
    p, s, u, F, J, w = RP.gens
    L_P, M_P = linear_coordinates(s, u, F, J, ms)
    a, b = L_P.diff(F), L_P.diff(J)
    c, d = M_P.diff(F), M_P.diff(J)
    is_linear = L_P == a * F + b * J and M_P == c * F + d * J and not any(
        e.diff(F) or e.diff(J) for e in (a, b, c, d)
    )
    det = a * d - b * c
    rep.record(
        "05a determinant of (F,J) -> (L,M) is 1",
        is_linear and det == 1,
        f"det = {det.as_expr()} (computed from the coefficient matrix over Z[p,s,u])",
    )
    F_back, J_back = linear_inverse(s, u, L_P, M_P, ms)
    rep.record("05b con:linear-inverse after con:linear-coordinates is the identity on F, J", F_back == F and J_back == J)
    bp, bs, bu, bM, bL, bw = RT.gens
    F_of_L, J_of_L = linear_inverse(bs, bu, bL, bM, ms)
    L_back, M_back = linear_coordinates(bs, bu, F_of_L, J_of_L, ms)
    rep.record("05c con:linear-coordinates after con:linear-inverse is the identity on L, M", L_back == bL and M_back == bM)


@step("06 con:h-expansion")
def check_h_expansion(ctx, rep):
    RT = ctx.RT
    bp, bs, bu, bM, bL, bw = RT.gens
    F_of_L, J_of_L = linear_inverse(bs, bu, bL, bM, ctx.ms)
    H_L = H_of(bp, bs, bu, F_of_L, J_of_L, ctx.ms)
    Q_L = Q_of(bs, bu, F_of_L, J_of_L)
    ctx.F_of_L, ctx.H_L, ctx.Q_L = F_of_L, H_L, Q_L
    ok = H_L == bL - bp * bu + bp**2 * Q_L + bp**4 * F_of_L**3
    p_divides = divide_by_gen_power(H_L - bL, bp, 1) is not None
    rep.record(
        "06 con:h-expansion",
        ok and p_divides and H_L.degree(bw) <= 0,
        f"H(L) = L - pu + p^2 Q(L) + p^4 F(L)^3 in B[L] (H(L): {len(H_L)} terms, deg_L {H_L.degree(bL)}; "
        f"Q(L): {len(Q_L)} terms); p | H(L) - L: {p_divides}",
    )


@step("07 con:root")
def check_root(ctx, rep):
    need(ctx, "Q_L")
    RT = ctx.RT
    bp, bs, bu, bM, bL, bw = RT.gens
    C = substitute(ctx.Q_L, RT, [bp, bs, bu, bM, RT.zero, bw])
    ok_c = C == C_displayed(bs, bu, bM)
    Q1 = divide_by_gen_power(ctx.Q_L - C, bL, 1)
    ok_q1 = Q1 is not None and bL * Q1 + C == ctx.Q_L
    ctx.C = C if ok_c else None
    ctx.Q1 = Q1 if ok_q1 else None
    rep.record("07a C = Q(0) = M^2(2x0 + 6 s x0^2 + 4 s^2 x0^3 - x0^4)", ok_c, f"C has {len(C)} terms")
    rep.record(
        "07b Q(L) - C is divisible by L in B[L]",
        ok_q1,
        f"Q1 has {len(Q1)} terms, deg_L {Q1.degree(bL)}" if Q1 is not None else "inexact",
    )


@step("08 con:root-divisibility")
def check_root_divisibility(ctx, rep):
    need(ctx, "C", "Q1", "H_L", "F_of_L")
    RT = ctx.RT
    bp, bs, bu, bM, bL, bw = RT.gens
    L_star = bp * bu - bp**2 * ctx.C
    ctx.L_star = L_star
    at_root = [bp, bs, bu, bM, L_star, None]
    H_root = substitute(ctx.H_L, RT, at_root)
    Q_root, Q1_root, F_root = (substitute(f, RT, at_root) for f in (ctx.Q_L, ctx.Q1, ctx.F_of_L))
    ctx.H_root = H_root
    ok_text = Q_root - ctx.C == L_star * Q1_root
    ok = H_root == bp**3 * ((bu - bp * ctx.C) * Q1_root + bp * F_root**3)
    in_p3B = divide_by_gen_power(H_root, bp, 3) is not None and H_root.degree(bL) <= 0
    rep.record(
        "08 con:root-divisibility",
        ok and ok_text and in_p3B,
        f"H(L*) = p^3((u - pC) Q1(L*) + p F(L*)^3) in p^3 B, with L* = pu - p^2 C "
        f"(H(L*): {len(H_root)} terms); Q(L*) - C = L* Q1(L*): {ok_text}",
    )


@step("09 con:e-polynomial")
def check_e_polynomial(ctx, rep):
    need(ctx, "Q1", "H_L", "Q_L", "F_of_L")
    RT = ctx.RT
    bp, bs, bu, bM, bL, bw = RT.gens
    F3 = ctx.F_of_L**3
    h = bu - bp * ctx.Q_L - bp**3 * F3 - bp**2 * bw
    e0 = ctx.ms.e0_w_coefficient * bw - bp * F3 - ctx.Q1 * h
    G = ctx.H_L + bp**3 * bw
    ctx.e0, ctx.G = e0, G
    rep.record(
        "09 con:e-polynomial",
        G == bL - bp * h,
        f"H(L) + p^3 w = L - p h (h: {len(h)} terms; e0: {len(e0)} terms, deg_L {e0.degree(bL)}, deg_w {e0.degree(bw)})",
    )


@step("10 con:e-certificate")
def check_e_certificate(ctx, rep):
    need(ctx, "e0", "G", "L_star", "Q1")
    bp, bs, bu, bM, bL, bw = ctx.RT.gens
    lhs = bp**3 * ctx.e0 - (bL - ctx.L_star)
    rep.record(
        "10 con:e-certificate",
        lhs == (bp**2 * ctx.Q1 - 1) * ctx.G,
        f"p^3 e0 - (L - L*) = (p^2 Q1(L) - 1)(H(L) + p^3 w) ({len(lhs)} terms)",
    )


@step("11 W(Z) = -H(L* + p^3 Z)/p^3")
def check_W(ctx, rep):
    need(ctx, "L_star", "H_L", "H_root", "G")
    RT, RZ = ctx.RT, ctx.RZ
    zp, zs, zu, zM, zZ = RZ.gens
    base = [zp, zs, zu, zM, None, None]
    L_sub = substitute(ctx.L_star, RZ, base) + zp**3 * zZ
    ctx.L_sub = L_sub
    H_shift = substitute(ctx.H_L, RZ, [zp, zs, zu, zM, L_sub, None])
    diff_ok = divide_by_gen_power(H_shift - substitute(ctx.H_root, RZ, base), zp, 3) is not None
    W_neg = divide_by_gen_power(H_shift, zp, 3)
    W = -W_neg if W_neg is not None else None
    ctx.W = W
    relation_ok = W is not None and not substitute(ctx.G, RZ, [zp, zs, zu, zM, L_sub, W])
    rep.record(
        "11 H(L* + p^3 Z) divisible by p^3 in B[Z]",
        diff_ok and W is not None and relation_ok,
        f"p^3 | H(L*+p^3Z) - H(L*): {diff_ok}; "
        + (f"W(Z) has {len(W)} terms, deg_Z {W.degree(zZ)}; " if W is not None else "W undefined; ")
        + f"H(L*+p^3Z) + p^3 W(Z) = 0: {relation_ok}",
    )


@step("12 round trip B[Z] -> T -> B[Z]")
def check_roundtrip_Z(ctx, rep):
    need(ctx, "e0", "W", "L_sub")
    zp, zs, zu, zM, zZ = ctx.RZ.gens
    back = substitute(ctx.e0, ctx.RZ, [zp, zs, zu, zM, ctx.L_sub, ctx.W])
    rep.record(
        "12 e0(L = L* + p^3 E, w = W(E)) = E",
        back == zZ,
        "exact expansion in Z[p,s,u,M,E]" + ("" if back == zZ else f"; got {len(back)} terms"),
    )


@step("13 round trip T -> B[Z] -> T")
def check_roundtrip_T(ctx, rep):
    need(ctx, "e0", "W", "G", "L_star", "Q1")
    RT = ctx.RT
    bp, bs, bu, bM, bL, bw = RT.gens
    rep.record(
        "13a L* + p^3 e0 - L = (p^2 Q1 - 1)(H + p^3 w)",
        ctx.L_star + bp**3 * ctx.e0 - bL == (bp**2 * ctx.Q1 - 1) * ctx.G,
        "image of L is L modulo H + p^3 w (identity 10)",
    )
    W_e0 = substitute(ctx.W, RT, [bp, bs, bu, bM, ctx.e0])
    D = W_e0 - bw
    q, reason = divide_linear_in(D, ctx.G, bw)
    if q is None:
        rep.record(
            "13b W(e0) - w = q (H + p^3 w)",
            False,
            f"W(e0) - w has {len(D)} terms, deg_w {D.degree(bw)}; division failed: {reason}",
        )
        return
    verified = q * ctx.G == D
    blob = canonical_json(q).encode("utf-8")
    rep.record(
        "13b W(e0) - w = q (H + p^3 w)",
        verified,
        f"W(e0) - w has {len(D)} terms, deg_w {D.degree(bw)}; q in Z[p,s,u,M,L,w] has {len(q)} terms, "
        f"deg_w {q.degree(bw)}; expansion q(H + p^3 w) matches; "
        f"sha256(q) = {hashlib.sha256(blob).hexdigest()} ({len(blob)} bytes)",
    )


# --------------------------------------------------------------------------
# Driver.
# --------------------------------------------------------------------------


def build_context(ms: Manuscript) -> SimpleNamespace:
    RP = ring("p,s,u,F,J,w", ZZ)[0]  # P[w]
    RL = ring("p,t,x,y,z,u", ZZ)[0]  # Z[p,p^-1,x,y,z,u] = Z[p,t,x,y,z,u]/(pt - 1)
    RT = ring("p,s,u,M,L,w", ZZ)[0]  # B[L,w], B = Z[p,s,u,M]
    RZ = ring("p,s,u,M,Z", ZZ)[0]  # B[Z]
    i_p, i_t = RL.index(RL.gens[0]), RL.index(RL.gens[1])
    return SimpleNamespace(
        ms=ms, RP=RP, RL=RL, RT=RT, RZ=RZ, lnf=lambda f: laurent_normal_form(f, i_p, i_t)
    )


def main(argv: Optional[Sequence[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--negative-control",
        choices=sorted(NEGATIVE_CONTROLS),
        help="perturb one manuscript constant; the script must then report RESULT: fails",
    )
    args = ap.parse_args(argv)
    overrides = NEGATIVE_CONTROLS.get(args.negative_control, {})
    ms = dataclasses.replace(Manuscript(), **overrides)

    print(
        f"[INFO] sympy {sympy.__version__} (ground types {GROUND_TYPES}); exact expansion over ZZ; "
        f"negative control: {args.negative_control or 'none'}"
        + (f" {overrides}" if overrides else ""),
        flush=True,
    )
    started = time.perf_counter()
    ctx = build_context(ms)
    rep = Report()
    for label, fn in STEPS:
        try:
            fn(ctx, rep)
        except Skip as exc:
            rep.skip(label, str(exc))
        except Exception as exc:  # any crash is a failed check, never a pass
            rep.record(label, False, f"exception {type(exc).__name__}: {exc}")
    elapsed = time.perf_counter() - started
    print(f"elapsed {elapsed:.1f}s", file=sys.stderr)

    summary = (
        f"{rep.passed} passed, {rep.failed} failed, {rep.skipped} skipped; "
        f"{rep.total} of {EXPECTED_RESULTS} expected results"
    )
    if rep.holds:
        print(f"RESULT: holds ({summary})")
        return 0
    print(f"RESULT: fails ({summary})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
