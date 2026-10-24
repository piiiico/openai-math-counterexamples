"""Exact parameter-specialization evidence for Family 199, Lemma res:base.

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Source commit 1581d4cbdd69a0faf34b2089614fe2a814316a6a; sources.json pins files.
This checks polynomial algebra identities and a declared finite domain of
specializations. PROOF.md, not this replay, gives the all-degree theorem.
No positive-characteristic root specialization is called a counterexample
to the source, which assumes transcendental q.
"""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass
from functools import reduce
from itertools import product
import json
from operator import xor
from pathlib import Path
import sys


class VerificationError(ValueError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def polynomial_mul(a: int, b: int) -> int:
    """Carryless product in F2[X], with coefficient bits as the representation."""
    result = 0
    while b:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result


@dataclass(frozen=True)
class BinaryField:
    modulus: int

    def __post_init__(self):
        if self.modulus < 3 or not self.modulus & 1:
            raise ValueError('modulus must have positive degree and constant term')
        # A finite commutative quotient is a field exactly when all nonzero
        # elements are units. Test the explicit Fermat inverses exhaustively.
        if any(self.mul(a, self.pow(a, self.size - 2)) != 1
               for a in range(1, self.size)):
            raise ValueError('reducible modulus')

    @property
    def size(self) -> int:
        return 1 << (self.modulus.bit_length() - 1)

    def mul(self, a: int, b: int) -> int:
        value = polynomial_mul(a, b)
        while value.bit_length() >= self.modulus.bit_length():
            value ^= self.modulus << (value.bit_length() - self.modulus.bit_length())
        return value

    def pow(self, a: int, n: int) -> int:
        if n < 0:
            raise ValueError('negative exponent')
        value = 1
        while n:
            if n & 1:
                value = self.mul(value, a)
            a = self.mul(a, a)
            n >>= 1
        return value

    def inv(self, a: int) -> int:
        if not a:
            raise ZeroDivisionError('zero has no inverse')
        return self.pow(a, self.size - 2)


def vector(basis: tuple[str, ...], terms: dict[str, int]) -> tuple[int, ...]:
    require(set(terms) <= set(basis), 'vector uses a basis element outside its space')
    return tuple(terms.get(a, 0) for a in basis)


class Algebra:
    """Bilinear table, independently interpreted from structured source data."""
    def __init__(self, data: dict, mul, evaluate):
        self.basis = tuple(row['name'] for row in data['basis'])
        require(len(set(self.basis)) == len(self.basis), 'duplicate basis')
        self.records = {row['name']: row for row in data['basis']}
        self.mul_scalar = mul
        self.table = {}
        for a in self.basis:
            row = self.records[a]
            self.table[row['left'], a] = {a: 1}
            self.table[a, row['right']] = {a: 1}
        for row in data['products']:
            pair = tuple(row['inputs'])
            require(len(pair) == 2 and set(pair) <= set(self.basis), 'invalid product')
            require(pair not in self.table, 'duplicate product')
            self.table[pair] = {a: evaluate(exponents) for a, exponents in row['output'].items()}
        for (a, b), out in self.table.items():
            for c, coefficient in out.items():
                require(c in self.records, 'unknown output')
                ra, rb, rc = self.records[a], self.records[b], self.records[c]
                require(ra['right'] == rb['left'] and ra['left'] == rc['left']
                        and rb['right'] == rc['right'], 'inconsistent corners')
                require(ra['degree'] + rb['degree'] == rc['degree'], 'inconsistent grading')

    def multiply(self, left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
        out = {}
        for a, ca in left.items():
            for b, cb in right.items():
                for c, cc in self.table.get((a, b), {}).items():
                    out[c] = out.get(c, 0) ^ self.mul_scalar(self.mul_scalar(ca, cb), cc)
        return {a: c for a, c in out.items() if c}

    def corner_basis(self, side: str, idempotent: str) -> tuple[str, ...]:
        return tuple(a for a in self.basis if self.records[a][side] == idempotent)

    def matrix(self, domain: tuple[str, ...], codomain: tuple[str, ...],
               factor: dict[str, int], *, left: bool = False) -> list[tuple[int, ...]]:
        return [vector(codomain, self.multiply(factor, {a: 1}) if left
                       else self.multiply({a: 1}, factor)) for a in domain]


def verify_polynomial_algebra(data: dict) -> dict:
    algebra = Algebra(data, polynomial_mul, lambda es: reduce(xor, (1 << i for i in es), 0))
    require(all(type(row['degree']) is int and
                (row['degree'] == 0 if row['name'] in data['idempotents'] else row['degree'] > 0)
                for row in data['basis']), 'positive radical grading')
    require(max(row['degree'] for row in data['basis']) <= 4, 'grading exceeds degree four')
    unit = {a: 1 for a in data['idempotents']}
    for a in algebra.basis:
        require(algebra.multiply(unit, {a: 1}) == {a: 1}, 'left unit')
        require(algebra.multiply({a: 1}, unit) == {a: 1}, 'right unit')
    for a, b, c in product(algebra.basis, repeat=3):
        left = algebra.multiply(algebra.multiply({a: 1}, {b: 1}), {c: 1})
        right = algebra.multiply({a: 1}, algebra.multiply({b: 1}, {c: 1}))
        require(left == right, f'polynomial associativity at {(a, b, c)}: {left} != {right}')
    return {'basis_triples': len(algebra.basis) ** 3, 'unit_checks': 2 * len(algebra.basis),
            'coefficient_ring': 'F2[q], exact coefficient bits', 'positive_grading_max': 4}


def apply_matrix(field: BinaryField, columns: list[tuple[int, ...]],
                 v: tuple[int, ...]) -> tuple[int, ...]:
    require(len(columns) == len(v), 'matrix domain mismatch')
    return tuple(reduce(xor, (field.mul(col[i], c) for col, c in zip(columns, v)), 0)
                 for i in range(len(columns[0])))


def rref(field: BinaryField, columns: list[tuple[int, ...]]):
    if not columns:
        return [], []
    rows = [list(row) for row in zip(*columns, strict=True)]
    pivots = []
    for column in range(len(columns)):
        pivot = next((i for i in range(len(pivots), len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        row = len(pivots)
        rows[row], rows[pivot] = rows[pivot], rows[row]
        inverse = field.inv(rows[row][column])
        rows[row] = [field.mul(inverse, x) for x in rows[row]]
        for i in range(len(rows)):
            if i != row and rows[i][column]:
                coefficient = rows[i][column]
                rows[i] = [a ^ field.mul(coefficient, b) for a, b in zip(rows[i], rows[row])]
        pivots.append(column)
    return rows, pivots


def rank(field: BinaryField, columns: list[tuple[int, ...]]) -> int:
    return len(rref(field, columns)[1])


def kernel(field: BinaryField, columns: list[tuple[int, ...]]) -> list[tuple[int, ...]]:
    rows, pivots = rref(field, columns)
    result = []
    for free in range(len(columns)):
        if free not in pivots:
            v = [0] * len(columns)
            v[free] = 1
            for row, pivot in enumerate(pivots):
                v[pivot] = rows[row][free]
            result.append(tuple(v))
    return result


def same_span(field, actual, expected, label):
    r = rank(field, expected)
    require(rank(field, actual) == r == rank(field, actual + expected), label)


def quotient_basis(field, outgoing, incoming, witnesses, label):
    ker = kernel(field, outgoing)
    for v in incoming + witnesses:
        require(not any(apply_matrix(field, outgoing, v)), label + ': not a cycle')
    require(rank(field, incoming + witnesses) == rank(field, incoming) + len(witnesses),
            label + ': dependent modulo boundaries')
    same_span(field, ker, incoming + witnesses, label + ': incomplete homology basis')
    return len(witnesses)


def verify_case(data: dict, field: BinaryField, q: int, maximum_degree: int) -> dict:
    require(0 <= q < field.size and maximum_degree >= 2, 'invalid finite domain')
    algebra = Algebra(data, field.mul, lambda es: reduce(xor, (field.pow(q, i) for i in es), 0))
    ce, cf = algebra.corner_basis('right', 'e'), algebra.corner_basis('right', 'f')
    ec, fc = algebra.corner_basis('left', 'e'), algebra.corner_basis('left', 'f')
    ell = lambda i: {'x': 1, 'y': field.pow(q, i)}
    vu = lambda basis, a: vector(basis, {a: 1})
    right_u = algebra.matrix(ce, cf, {'u': 1})
    left_u = algebra.matrix(fc, ec, {'u': 1}, left=True)
    right = [algebra.matrix(ce, ce, ell(i)) for i in range(maximum_degree)]
    left = [algebra.matrix(ec, ec, ell(i), left=True) for i in range(maximum_degree)]

    # Expected coordinate spaces are compared against Gaussian elimination of
    # matrices obtained by multiplying the full source algebra table.
    same_span(field, right_u, [vu(cf, a) for a in ('u', 'v') + (() if q == 1 else ('n',))],
              'right u image')
    same_span(field, kernel(field, right_u), [vector(ce, ell(0)), vu(ce, 'z'), vu(ce, 'j')]
              + ([vu(ce, 't')] if q == 1 else []), 'right u kernel')
    require(rank(field, left_u) == 4, 'left u must be injective')
    for i, (r, l) in enumerate(zip(right, left)):
        singular = field.pow(q, i + 2) == 1
        same_span(field, r, [vector(ce, ell(i)), vu(ce, 'z')]
                  + ([] if singular else [vu(ce, 'j')]), f'right image {i}')
        same_span(field, kernel(field, r), [vector(ce, ell(i + 1)), vu(ce, 'z'), vu(ce, 'j')]
                  + ([vu(ce, 't')] if singular else []), f'right kernel {i}')
        if i == 0:
            kexpected = [vector(ec, {'x': q, 'y': 1})] + [vu(ec, a) for a in ('z', 'u', 'v')]
            iexpected = [vector(ec, ell(0)), vu(ec, 'z')]
        elif q == 0:
            kexpected = [vu(ec, a) for a in ('x', 'y', 'z', 'v')]
            iexpected = [vu(ec, a) for a in ('x', 'v')]
        else:
            kexpected = [vector(ec, ell(i - 1)), vu(ec, 'z'), vu(ec, 'v')]
            iexpected = [vector(ec, ell(i)), vu(ec, 'z')]
            if field.pow(q, i) == 1:
                kexpected.append(vu(ec, 'u'))
            else:
                iexpected.append(vu(ec, 'v'))
        same_span(field, kernel(field, l), kexpected, f'left kernel {i}')
        same_span(field, l, iexpected, f'left image {i}')

    epsilon = [(int(a == 'f'),) for a in cf]
    chain = [quotient_basis(field, epsilon, right_u,
                           [vu(cf, 'n')] if q == 1 else [], 'augmentation')]
    chain.append(quotient_basis(field, right_u, right[0],
                               [vu(ce, a) for a in ('t', 'j')] if q == 1 else [], 'degree 1'))
    for n in range(2, maximum_degree + 1):
        ws = ([vu(ce, 't')] if field.pow(q, n) == 1 else [])
        ws += ([vu(ce, 'j')] if field.pow(q, n + 1) == 1 else [])
        chain.append(quotient_basis(field, right[n - 2], right[n - 1], ws, f'chain degree {n}'))
    dual = [len(fc) - rank(field, left_u), quotient_basis(field, left[0], left_u, [], 'dual degree 1')]
    for n in range(2, maximum_degree + 1):
        if q == 0:
            ws = [vu(ec, a) for a in (('x', 'v') if n == 2 else ('y', 'z'))]
        else:
            ws = ([vu(ec, 'u')] if field.pow(q, n - 1) == 1 else [])
            ws += ([vu(ec, 'v')] if field.pow(q, n - 2) == 1 else [])
        dual.append(quotient_basis(field, left[n - 1], left[n - 2], ws, f'dual degree {n}'))
    order = next((n for n in range(1, field.size) if field.pow(q, n) == 1), None)
    return {'field_size': field.size, 'modulus_bits': field.modulus, 'q_bits': q,
            'order': order, 'maximum_degree': maximum_degree,
            'chain_homology_dimensions': chain, 'dual_cohomology_dimensions': dual}


def run(data: dict, negative_control: str | None = None) -> dict:
    if negative_control == 'product':
        data = copy.deepcopy(data)
        next(p for p in data['products'] if p['inputs'] == ['t', 'y'])['output']['j'] = [1]
    polynomial = verify_polynomial_algebra(data)
    cases = []
    for modulus in (0b11, 0b111, 0b1011, 0b10011):
        field = BinaryField(modulus)
        for q in range(field.size):
            case = verify_case(data, field, q, 2 * (field.size - 1) + 2)
            cases.append(case)
            if negative_control == 'root' and case['order'] not in (None, 1):
                require(not any(case['chain_homology_dimensions']),
                        'false root-of-unity exactness rejected by computed homology')
            if negative_control == 'zero-dual' and q == 0:
                expected = [int(n == 2) for n in range(case['maximum_degree'] + 1)]
                require(case['dual_cohomology_dimensions'] == expected,
                        'false generic dual profile at q=0 rejected by computed cohomology')
    return {'scope': 'finite specializations; uniform classification is a written proof',
            'polynomial_algebra': polynomial, 'case_count': len(cases),
            'degrees_per_complex': sum(c['maximum_degree'] + 1 for c in cases), 'cases': cases}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path(__file__).with_name('algebra.json'))
    parser.add_argument('--report', type=Path)
    parser.add_argument('--negative-control', choices=('product', 'root', 'zero-dual'))
    args = parser.parse_args()
    try:
        result = run(json.loads(args.data.read_text()), args.negative_control)
    except (VerificationError, ValueError, KeyError) as error:
        print(f'REJECT: {error}', file=sys.stderr)
        return 1
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + '\n')
    print(f"RESULT: 1000 polynomial associativity identities; {result['case_count']} exact field/parameter cases; "
          f"{result['degrees_per_complex']} degrees in each complex; all kernel/image and homology witnesses agree.")
    print('SCOPE: augmentation defects and Hom-complex cohomology; Ext only when the displayed resolution is exact.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
