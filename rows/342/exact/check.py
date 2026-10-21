#!/usr/bin/env python3
"""Exact algebra for Family 342, Example ex:strict-cones (not a cone theorem).

Derived from openai/math@1581d4cbdd69a0faf34b2089614fe2a814316a6a,
preprints/Taming-implies-compatibility-on-four-manifolds-October-6-2026/
build/sections/08-cones.tex:375-418. See README.md for source hashes and scope.

Independent implementation by Alexander Richard Towell, with substantial
OpenAI Codex assistance. Credits: OpenAI's example and Pico/Håkon Åmdal's
previous sampled replay. All calculations use integer polynomials; no grid,
finite differences, floats, or source checker code. Original code: MIT.
"""
from dataclasses import dataclass
from fractions import Fraction
from itertools import permutations
import argparse


@dataclass(frozen=True)
class Poly:
    """Canonical sparse elements of Z[f,k,z]."""
    terms: tuple

    @classmethod
    def make(cls, terms):
        return cls(tuple(sorted((m, c) for m, c in terms.items() if c)))

    @classmethod
    def constant(cls, c):
        return cls.make({(0, 0, 0): c})

    @staticmethod
    def coerce(value):
        if isinstance(value, Poly):
            return value
        if isinstance(value, int):
            return Poly.constant(value)
        raise TypeError('polynomial coefficients must be integers')

    def __add__(self, other):
        out = dict(self.terms)
        for m, c in self.coerce(other).terms:
            out[m] = out.get(m, 0) + c
        return self.make(out)

    __radd__ = __add__

    def __neg__(self):
        return self.make({m: -c for m, c in self.terms})

    def __sub__(self, other):
        return self + -self.coerce(other)

    def __rsub__(self, other):
        return self.coerce(other) + -self

    def __mul__(self, other):
        out = {}
        for m, c in self.terms:
            for n, d in self.coerce(other).terms:
                p = tuple(a + b for a, b in zip(m, n))
                out[p] = out.get(p, 0) + c*d
        return self.make(out)

    __rmul__ = __mul__

    def __pow__(self, n):
        if not isinstance(n, int) or n < 0:
            raise ValueError('nonnegative integer exponent required')
        result = self.constant(1)
        for _ in range(n):
            result = result * self
        return result

    def derivative(self, variable):
        out = {}
        for m, c in self.terms:
            if m[variable]:
                p = list(m)
                p[variable] -= 1
                out[tuple(p)] = c*m[variable]
        return self.make(out)

    def at(self, values):
        return sum(c * values[0]**m[0] * values[1]**m[1] * values[2]**m[2]
                   for m, c in self.terms)


def variables():
    return tuple(Poly.make({tuple(int(i == j) for i in range(3)): 1})
                 for j in range(3))


ZERO = Poly.constant(0)
ONE = Poly.constant(1)


def identity(n):
    return tuple(tuple(ONE if i == j else ZERO for j in range(n)) for i in range(n))


def transpose(a):
    return tuple(zip(*a))


def add(a, b):
    return tuple(tuple(x + y for x, y in zip(r, s)) for r, s in zip(a, b))


def scale(c, a):
    return tuple(tuple(c*x for x in row) for row in a)


def multiply(a, b):
    return tuple(tuple(sum((x*y for x, y in zip(r, s)), ZERO)
                       for s in transpose(b)) for r in a)


def permutation_sign(p):
    return (-1)**sum(p[i] > p[j] for i in range(len(p)) for j in range(i+1, len(p)))


def determinant(a):
    result = ZERO
    for p in permutations(range(len(a))):
        term = Poly.constant(permutation_sign(p))
        for i, j in enumerate(p):
            term = term*a[i][j]
        result = result + term
    return result


def form(terms):
    a = [[ZERO for _ in range(4)] for _ in range(4)]
    for (i, j), c in terms.items():
        a[i][j] = Poly.coerce(c)
        a[j][i] = -Poly.coerce(c)
    return tuple(tuple(row) for row in a)


def wedge_basis(a, b):
    indices = a + b
    if len(set(indices)) != len(indices):
        return None
    return tuple(sorted(indices)), permutation_sign(indices)


def coefficients(a):
    return {(i, j): a[i][j] for i in range(4) for j in range(i+1, 4)}


def wedge(a, b):
    out = {}
    for p, c in a.items():
        for q, d in b.items():
            term = wedge_basis(p, q)
            if term is not None:
                indices, sign = term
                out[indices] = out.get(indices, ZERO) + sign*c*d
    return {p: c for p, c in out.items() if c != ZERO}


def star(a):
    out = {}
    for p, c in coefficients(a).items():
        q = tuple(i for i in range(4) if i not in p)
        out[q] = permutation_sign(p+q)*c
    return form(out)


def exterior_derivative(a, variable, coordinate):
    """Coefficient of the independent derivative f' or k' in d(a)."""
    return wedge({(coordinate,): ONE},
                 {p: c.derivative(variable) for p, c in coefficients(a).items()})


def definitions(eta_factor=2):
    f, k, z = variables()
    u = form({(0, 1): 1, (2, 3): 1})
    v = form({(0, 2): 1, (1, 3): -1})
    w = form({(0, 3): 1, (1, 2): 1})
    n = add(add(u, scale(f, v)), scale(k, w))
    eta = add(u, form({(0, 2): eta_factor*f, (1, 2): eta_factor*k}))
    return f, k, z, u, v, w, n, eta


def closure_check(swapped=False):
    *_, eta = definitions()
    supports = (1, 0) if swapped else (0, 1)
    return all(not exterior_derivative(eta, var, coordinate)
               for var, coordinate in enumerate(supports))


def taming_margin(amplitude):
    """Numerator min(1+f,1-f) for -amplitude <= f <= amplitude."""
    if amplitude < 0:
        raise ValueError('amplitude must be nonnegative')
    return 1 - amplitude


def verify(eta_factor=2):
    f, k, z, u, v, w, n, eta = definitions(eta_factor)
    ident = identity(4)
    s = f*f + k*k
    r2 = 1+s
    metric = scale(-1, multiply(eta, n))  # r * eta(X,JY), J=-N/r
    centered = add(metric, scale(-r2, ident))
    asd = form({(0, 2): f, (1, 3): f, (1, 2): k, (0, 3): -k})
    obligations = {
        'basis_self_dual': all(star(b) == b for b in (u, v, w)),
        'N_self_dual': star(n) == n,
        'N_square': multiply(n, n) == scale(-r2, ident),
        'N_norm': sum((c*c for c in coefficients(n).values()), ZERO) == 2*r2,
        'eta_self_dual_part': add(eta, star(eta)) == scale(2, n),
        'eta_anti_self_dual_part': add(eta, scale(-1, star(eta))) == scale(2, asd),
        'eta_invariant': multiply(multiply(transpose(n), eta), n) == scale(r2, eta),
        'eta_metric_symmetric': metric == transpose(metric),
        'eta_metric_square': multiply(centered, centered) == scale(r2*s, ident),
        'eta_characteristic_polynomial': determinant(add(scale(z, ident), scale(-1, metric))) == ((z-r2)**2-r2*s)**2,
        'eta_closed_separated_support': closure_check(),
    }
    for sign, label in [(1, 'plus'), (-1, 'minus')]:
        b = add(u, scale(sign, v))
        bj = scale(-1, multiply(b, n))
        obligations['taming_'+label] = add(bj, transpose(bj)) == scale(2*(1+sign*f), ident)
        obligations['invariant_projection_'+label] = add(scale(r2, b), multiply(multiply(transpose(n), b), n)) == scale(2*(1+sign*f), n)
    for basis, coefficient, label in [(v, f, 'V'), (w, k, 'W')]:
        perpendicular = add(basis, scale(-coefficient, u))
        obligations['anti_invariant_perp_'+label] = multiply(multiply(transpose(n), perpendicular), n) == scale(-r2, perpendicular)
    obligations['zero_mixed_pairing'] = not wedge(coefficients(add(u, v)), coefficients(add(u, scale(-1, v))))
    obligations['positive_self_pairings'] = all(wedge(coefficients(add(u, scale(sign, v))), coefficients(add(u, scale(sign, v)))) == {(0, 1, 2, 3): Poly.constant(4)} for sign in (1, -1))
    # Constant self-dual candidates at f,k = (0,0),(1/4,0),(0,1/4).
    # Scale each row by 4 to keep the ring integral: determinant 4, hence 1/16 originally.
    obligations['three_point_span'] = determinant(tuple(tuple(Poly.constant(c) for c in row) for row in [(4,0,0),(4,1,0),(4,0,1)])) == Poly.constant(4)
    return obligations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control', choices=['eta-factor', 'derivative-support', 'taming-amplitude'])
    args = parser.parse_args()
    obligations = verify(eta_factor=1 if args.negative_control == 'eta-factor' else 2)
    if args.negative_control == 'derivative-support':
        obligations['eta_closed_separated_support'] = closure_check(swapped=True)
    if args.negative_control == 'taming-amplitude':
        obligations['positive_taming_numerator'] = taming_margin(Fraction(5, 4)) > 0
    else:
        obligations['positive_taming_numerator'] = taming_margin(Fraction(1, 4)) > 0
    for name, ok in obligations.items():
        print(('PASS ' if ok else 'FAIL ') + name)
    passed = all(obligations.values())
    print('RESULT: exact all-parameter identities verified' if passed else 'RESULT: rejected')
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
