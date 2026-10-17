#!/usr/bin/env python3
"""Integer certificates for the Family 049 companion, including its critical section.

Source: openai/math 1581d4cbdd69a0faf34b2089614fe2a814316a6a,
An-explicit-noncoordinate-polynomial-with-affine-three-space-zero-fibre-
September-24-2026/build/paper.tex:87-111,164-245,255-325,345-375.
Checks division-free identities over ZZ, not a finite-field inference.
The universal-ring and non-coordinate implications are written in PROOF.md.

Copyright 2026 Alexander Richard Towell. MIT licensed; see LICENSE.
Substantial OpenAI Codex assistance. Predecessors are credited in README.md.
"""
import argparse
from dataclasses import dataclass, replace
from itertools import product
import json
import sys

import sympy as sp


@dataclass(frozen=True)
class Inputs:
    cusp_leading: int = 2
    bezout_tail: int = 4
    inverse_cross: int = 2
    critical_point: tuple = (2, 1, -1, 1)


def source_polynomials(h, u, v, w, inputs):
    x = u**3+h*v
    y = -u**2+h*w
    s = inputs.cusp_leading*u**3*v+3*u**4*w+h*(v**2-3*u**2*w**2)+h**2*w**3
    p = -2*s**2*x+3*s*y**2-3*s**3*y
    return x, y, s, h-p-1


def bezout(x, y, s, inputs):
    alpha = 1+2*s**2*x+inputs.bezout_tail*s**5
    beta = (3*s**3-3*s*y)*(1+2*s**2*x)-4*s**4*y**2
    return alpha, beta


def verify(inputs=Inputs()):
    """Return exact certificate metadata, raising ValueError on any failed obligation."""
    records = []

    def identity(name, variables, lhs, rhs=0):
        left = sp.Poly(lhs, *variables, domain=sp.ZZ)
        right = sp.Poly(rhs, *variables, domain=sp.ZZ)
        residual = left-right
        if not residual.is_zero:
            raise ValueError(f'{name}: nonzero integer polynomial residual')
        records.append({'name': name, 'variables': [str(x) for x in variables],
                        'lhs_terms': len(left.terms()) if not left.is_zero else 0,
                        'rhs_terms': len(right.terms()) if not right.is_zero else 0,
                        'residual_terms': 0})

    h, u, v, w = sp.symbols('h u v w')
    ambient = (h, u, v, w)
    xR, yR, sR, F = source_polynomials(*ambient, inputs)
    identity('source cusp', ambient, xR**2+yR**3, h*sR)

    x, y, s, alpha, beta, U, G, W, T = sp.symbols('x y s alpha beta U G W T')
    base = (h, x, y, s)
    p = -2*s**2*x+3*s*y**2-3*s**3*y
    H = h-1-p
    D = x**2+y**3-h*s
    X, Y = x+s**3, y-s**2
    identity('base shift', base, X**2+Y**3-s, D+s*H)
    a0, b0 = bezout(x, y, s, inputs)
    identity('base Bezout', base, a0*h+b0*y-1, (1+2*s**2*x)*H-4*s**4*D)

    generic = (h, x, y, s, alpha, beta, U, G, W, T)
    E = alpha*h+beta*y-1
    g1 = h*G-y*U-x
    a = y+U**2
    b = s-h*G**2+inputs.inverse_cross*U*y*G
    g2, g3 = h*W-a, y**2*W-b
    _, _, S, _ = source_polynomials(h, U, G-U*W, W, inputs)
    identity('lifting first relation', generic, U**3+h*(G-U*W)-x, g1-U*g2)
    identity('lifting third relation', generic, S-s,
             g3+g2*(-2*U*G+2*y*W+W*g2))
    compat = D+g1*(h*G-y*U+x)
    identity('lifting compatibility', generic, y**2*a-h*b, compat)
    r, q = alpha*(1+beta*y), beta**2
    defect = E*(1+beta*y)
    identity('lifting unit ideal', generic, r*h+q*y**2-1, defect)
    W0 = r*a+q*b
    identity('lifting W solves h-equation', generic, h*W0-a, defect*a-q*compat)
    identity('lifting W solves y-squared-equation', generic, y**2*W0-b, r*compat+defect*b)
    identity('lifting ideal elimination', generic, W-W0, r*g2+q*g3-defect*W)

    U0, G0 = h*T-beta*x, y*T+alpha*x
    identity('parameter satisfies line', generic, h*G0-y*U0-x, x*E)
    identity('parameter round trip', generic, alpha*U0+beta*G0-T, T*E)
    T0 = alpha*U+beta*G
    identity('inverse U round trip', generic, h*T0-beta*x-U, U*E+beta*g1)
    identity('inverse G round trip', generic, y*T0+alpha*x-G, G*E-alpha*g1)

    fpoly = sp.Poly(F, *ambient, domain=sp.ZZ)
    if (len(inputs.critical_point) != 4 or
            any(type(x) is not int for x in inputs.critical_point)):
        raise ValueError('critical point must contain four integers')
    point = dict(zip(ambient, inputs.critical_point))
    values = [int(sp.Poly(f, *ambient, domain=sp.ZZ).as_expr().subs(point))
              for f in (xR, yR, sR, F)]
    gradient = [int(fpoly.diff(z).as_expr().subs(point)) for z in ambient]
    if values != [-1, 1, 1, -1] or gradient != [0, 0, 0, 0]:
        raise ValueError('integral critical section is not certified')
    records.append({'name': 'integral critical section', 'point': list(inputs.critical_point),
                    'x_y_s_F': values, 'gradient': gradient})
    return {'status': 'certified integer polynomial identities', 'domain': 'ZZ',
            'obligations': records, 'count': len(records),
            'F_degree': int(fpoly.total_degree()), 'F_terms': len(fpoly.terms()),
            'assumptions_for_noncoordinate_conclusion': 'commutative unital base ring with 1 != 0',
            'scope': 'September 24 companion; written universal-ring argument in PROOF.md; not a Lean proof'}


def to_fibre(X, Y, T, modulus, inputs=Inputs()):
    s = X**2+Y**3
    x, y = X-s**3, Y+s**2
    h = 1-2*s**2*x+3*s*y**2-3*s**3*y
    alpha, beta = bezout(x, y, s, inputs)
    u, g = h*T-beta*x, y*T+alpha*x
    w = alpha*(1+beta*y)*(y+u**2)+beta**2*(s-h*g**2+inputs.inverse_cross*u*y*g)
    return tuple(z % modulus for z in (h, u, g-u*w, w))


def from_fibre(point, modulus, inputs=Inputs()):
    h, u, v, w = point
    x, y, s, _ = source_polynomials(h, u, v, w, inputs)
    alpha, beta = bezout(x, y, s, inputs)
    return tuple(z % modulus for z in (x+s**3, y-s**2, alpha*u+beta*(v+u*w)))


def finite_controls(moduli=(2, 3, 4, 5, 6, 8, 9), inputs=Inputs()):
    """Complete finite-ring controls; the universal proof uses integer identities."""
    reports = []
    for modulus in moduli:
        if type(modulus) is not int or modulus < 2:
            raise ValueError('finite control needs an integer modulus at least two')
        for point in product(range(modulus), repeat=3):
            fibre = to_fibre(*point, modulus, inputs)
            if source_polynomials(*fibre, inputs)[3] % modulus != 0:
                raise ValueError('finite forward map misses the zero fibre')
            if from_fibre(fibre, modulus, inputs) != point:
                raise ValueError('finite parameter round trip failed')
        count = 0
        for point in product(range(modulus), repeat=4):
            if source_polynomials(*point, inputs)[3] % modulus == 0:
                count += 1
                if to_fibre(*from_fibre(point, modulus, inputs), modulus, inputs) != point:
                    raise ValueError('finite fibre round trip failed')
        if count != modulus**3:
            raise ValueError('finite zero fibre cardinality failed')
        reports.append({'modulus': modulus, 'parameter_points': modulus**3,
                        'ambient_points': modulus**4, 'zero_fibre_points': count})
    if not reports:
        raise ValueError('finite control domain must be nonempty')
    return reports


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--finite-controls', action='store_true')
    parser.add_argument('--negative-control', choices=['cusp', 'bezout', 'inverse', 'point'])
    args = parser.parse_args(argv)
    inputs = Inputs()
    if args.negative_control == 'cusp':
        inputs = replace(inputs, cusp_leading=3)
    elif args.negative_control == 'bezout':
        inputs = replace(inputs, bezout_tail=5)
    elif args.negative_control == 'inverse':
        inputs = replace(inputs, inverse_cross=3)
    elif args.negative_control == 'point':
        inputs = replace(inputs, critical_point=(2, 1, -1, 0))
    try:
        result = verify(inputs)
        if args.finite_controls:
            result['finite_controls'] = finite_controls(inputs=inputs)
    except ValueError as error:
        print(f'RESULT: not certified ({error})', file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    print('RESULT: certified integer polynomial identities and integral critical section')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
