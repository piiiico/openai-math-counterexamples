#!/usr/bin/env python3
"""Separate FLINT/dual-arithmetic replay supplied by the scoped AI reviewer.

No imports from SymPy or the primary checker. Main-agent edits replace review
assertions with explicit failures and add deliberate-input negative controls.
Copyright 2026 Alexander Richard Towell. MIT; see LICENSE.
Substantial OpenAI Codex assistance. See README.md for source credit and scope.
"""
import argparse
from itertools import product
import json
import sys

from flint import fmpz_mpoly_ctx


def require(condition, message):
    if not condition:
        raise ValueError(message)


def polynomial_replay(corrupt=False):
    def S(h, u, v, w):
        return (3 if corrupt else 2)*u**3*v+3*u**4*w+h*(v**2-3*u**2*w**2)+h**2*w**3

    Q = fmpz_mpoly_ctx.get(('h', 'u', 'v', 'w'), 'lex')
    h, u, v, w = Q.gens()
    x, y = u**3+h*v, -u**2+h*w
    require(x*x+y**3 == h*S(h, u, v, w), 'FLINT cusp identity failed')

    R = fmpz_mpoly_ctx.get(
        ('h', 'x', 'y', 's', 'alpha', 'beta', 'U', 'G', 'W', 'T'), 'lex')
    h, x, y, s, alpha, beta, U, G, W, T = R.gens()
    p = -2*s*s*x+3*s*y*y-3*s**3*y
    H, D, E = h-1-p, x*x+y**3-h*s, alpha*h+beta*y-1
    alpha0 = 1+2*s*s*x+4*s**5
    beta0 = (3*s**3-3*s*y)*(1+2*s*s*x)-4*s**4*y*y
    g1 = h*G-y*U-x
    a, b = y+U*U, s-h*G*G+2*U*y*G
    g2, g3 = h*W-a, y*y*W-b
    compat = D+g1*(h*G-y*U+x)
    r, q = alpha*(1+beta*y), beta*beta
    defect = E*(1+beta*y)
    W0 = r*a+q*b
    U0, G0, T0 = h*T-beta*x, y*T+alpha*x, alpha*U+beta*G
    checks = [
        ((x+s**3)**2+(y-s*s)**3-s, D+s*H),
        (alpha0*h+beta0*y-1, (1+2*s*s*x)*H-4*s**4*D),
        (U**3+h*(G-U*W)-x, g1-U*g2),
        (S(h,U,G-U*W,W)-s, g3+g2*(-2*U*G+2*y*W+W*g2)),
        (y*y*a-h*b, compat),
        (r*h+q*y*y-1, defect),
        (h*W0-a, defect*a-q*compat),
        (y*y*W0-b, r*compat+defect*b),
        (W-W0, r*g2+q*g3-defect*W),
        (h*G0-y*U0-x, x*E),
        (alpha*U0+beta*G0-T, T*E),
        (h*T0-beta*x-U, U*E+beta*g1),
        (y*T0+alpha*x-G, G*E-alpha*g1),
    ]
    for index, (left, right) in enumerate(checks, start=2):
        require(left == right, f'FLINT identity {index} failed')
    return 1+len(checks)


def dual_ring(modulus=0):
    class D:
        def __init__(self, a=0, b=0):
            self.a, self.b = ((a % modulus, b % modulus) if modulus else (a, b))

        @staticmethod
        def lift(x):
            return x if isinstance(x, D) else D(x)

        def __add__(self, other):
            other = D.lift(other)
            return D(self.a+other.a, self.b+other.b)

        __radd__ = __add__

        def __neg__(self):
            return D(-self.a, -self.b)

        def __sub__(self, other):
            return self+-D.lift(other)

        def __rsub__(self, other):
            return D.lift(other)+-self

        def __mul__(self, other):
            other = D.lift(other)
            return D(self.a*other.a, self.a*other.b+self.b*other.a)

        __rmul__ = __mul__

        def __pow__(self, n):
            answer = D(1)
            for _ in range(n):
                answer = answer*self
            return answer

        def __eq__(self, other):
            other = D.lift(other)
            return (self.a, self.b) == (other.a, other.b)
    return D


def data(h, u, v, w):
    x, y = u**3+h*v, -u**2+h*w
    s = 2*u**3*v+3*u**4*w+h*(v**2-3*u**2*w**2)+h**2*w**3
    p = -2*s**2*x+3*s*y**2-3*s**3*y
    return x, y, s, h-p-1


def bezout(x, y, s):
    return (1+2*s**2*x+4*s**5,
            (3*s**3-3*s*y)*(1+2*s**2*x)-4*s**4*y**2)


def forward(point):
    h, u, v, w = point
    x, y, s, _ = data(*point)
    a, b = bezout(x, y, s)
    return x+s**3, y-s**2, a*u+b*(v+u*w)


def backward(point, corrupt=False):
    X, Y, T = point
    s = X**2+Y**3
    x, y = X-s**3, Y+s**2
    h = 1-2*s**2*x+3*s*y**2-3*s**3*y
    a, b = bezout(x, y, s)
    u, g = h*T-b*x, y*T+a*x
    w = a*(1+b*y)*(y+u**2)+b**2*(s-h*g**2+2*u*y*g)
    if corrupt:
        w = w+1
    return h, u, g-u*w, w


def dual_replay(point=(2, 1, -1, 1), corrupt_inverse=False):
    D = dual_ring()
    gradient = []
    for k in range(4):
        result = data(*(D(a, int(i == k)) for i, a in enumerate(point)))[3]
        require(result.a == -1, 'dual critical value failed')
        gradient.append(result.b)
    require(data(*point) == (-1, 1, 1, -1), 'dual critical data failed')
    require(gradient == [0, 0, 0, 0], 'dual critical gradient failed')
    reports = []
    for prime in (2, 3):
        D = dual_ring(prime)
        ring = tuple(D(a, b) for a, b in product(range(prime), repeat=2))
        require(D(0, 1) != 0 and D(0, 1)**2 == 0, 'nonreduced-ring sanity failed')
        for parameter in product(ring, repeat=3):
            image = backward(parameter, corrupt_inverse)
            require(data(*image)[3] == 0, 'dual inverse misses zero fibre')
            require(forward(image) == parameter, 'dual parameter round trip failed')
        count = 0
        for ambient in product(ring, repeat=4):
            if data(*ambient)[3] == 0:
                require(backward(forward(ambient), corrupt_inverse) == ambient,
                        'dual fibre round trip failed')
                count += 1
        require(count == len(ring)**3, 'dual zero fibre count failed')
        reports.append({'ring': f'F{prime}[e]/(e^2)', 'parameter_points': len(ring)**3,
                        'ambient_points': len(ring)**4, 'zero_fibre_points': count})
    return {'point': list(point), 'F': -1, 'gradient': gradient, 'finite_rings': reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control', choices=['identity', 'point', 'inverse'])
    args = parser.parse_args()
    try:
        count = polynomial_replay(args.negative_control == 'identity')
        point = (2, 1, -1, 0) if args.negative_control == 'point' else (2, 1, -1, 1)
        report = dual_replay(point, args.negative_control == 'inverse')
    except ValueError as error:
        print(f'RESULT: independent replay rejected ({error})', file=sys.stderr)
        return 1
    report['integer_polynomial_identities'] = count
    print(json.dumps(report, indent=2, sort_keys=True))
    print('RESULT: independent replay passed (FLINT identities and dual arithmetic)')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
