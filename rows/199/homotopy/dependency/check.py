"""Family 199: exact finite identities in Lemma coc:data, not the full theorem.

Alexander Richard Towell, with substantial OpenAI Codex assistance.
Source: OpenAI math 1581d4cbdd69a0faf34b2089614fe2a814316a6a;
03-algebra.tex:12-120, 166-212 and 09-cochain.tex:19-38, 47-127. See sources.json.
Scalars are finite sets of (q exponent, H exponent), over F_2[q,H,H^-1].
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from functools import lru_cache
from itertools import product
import json
from pathlib import Path
import sys

Poly = frozenset[tuple[int, int]]
Vector = dict[str, Poly]
Cochain = dict[tuple[str, str, str], Vector]
ZERO: Poly = frozenset()


def monomial(q: int = 0, h: int = 0) -> Poly:
    return frozenset({(q, h)})


ONE, Q, H = monomial(), monomial(1), monomial(0, 1)


def add(a: Poly, b: Poly) -> Poly:
    return a ^ b


@lru_cache(maxsize=None)
def mul(a: Poly, b: Poly) -> Poly:
    terms = set()
    for aq, ah in a:
        for bq, bh in b:
            term = (aq + bq, ah + bh)
            if term in terms:
                terms.remove(term)
            else:
                terms.add(term)
    return frozenset(terms)


def accumulate(out: dict, key, coefficient: Poly) -> None:
    value = add(out.get(key, ZERO), coefficient)
    if value:
        out[key] = value
    else:
        out.pop(key, None)


def scale(v: Vector, coefficient: Poly) -> Vector:
    return {a: value for a, c in v.items() if (value := mul(c, coefficient))}


def sum_vectors(*vectors: Vector) -> Vector:
    result: Vector = {}
    for v in vectors:
        for a, coefficient in v.items():
            accumulate(result, a, coefficient)
    return result


def unit(a: str) -> Vector:
    return {a: ONE}


class InvalidData(ValueError):
    pass


class IdentityFailure(ValueError):
    def __init__(self, stage: str, inputs, residual: dict):
        self.stage, self.inputs, self.residual = stage, inputs, residual
        super().__init__(f'{stage} at {inputs}: {encode(residual)}')


def encode(v: dict) -> dict:
    return {str(k): sorted(coefficient) for k, coefficient in v.items()}


@dataclass
class Algebra:
    basis: tuple[str, ...]
    idempotents: tuple[str, ...]
    corners: dict[str, tuple[str, str]]
    degree: dict[str, int]
    dual: dict[str, str]
    weight: dict[str, int]
    table: dict[tuple[str, str], Vector]

    @property
    def radical(self) -> tuple[str, ...]:
        return tuple(a for a in self.basis if a not in self.idempotents)

    def multiply(self, left: Vector, right: Vector) -> Vector:
        result: Vector = {}
        for a, ca in left.items():
            for b, cb in right.items():
                coefficient = mul(ca, cb)
                for v, cv in self.table.get((a, b), {}).items():
                    accumulate(result, v, mul(coefficient, cv))
        return result


def require(condition: bool, message: str) -> None:
    if not condition:
        raise InvalidData(message)


def load_data(data: dict) -> tuple[Algebra, Cochain, frozenset[str]]:
    """Validate the transcription and derive DC actions by evaluating duals."""
    records = data['basis']
    lower = tuple(b['name'] for b in records)
    idem = tuple(data['idempotents'])
    require(len(set(lower)) == len(lower), 'duplicate basis name')
    require(all(isinstance(a, str) and len(a) == 1 and a.islower()
                and a.isascii() for a in lower), 'invalid basis name')
    require(len(set(idem)) == len(idem) and set(idem) <= set(lower),
            'invalid idempotents')
    corners = {b['name']: (b['left'], b['right']) for b in records}
    degree = {b['name']: b['degree'] for b in records}
    require(all(set(c) <= set(idem) for c in corners.values()), 'unknown corner')
    require(all(type(d) is int and d >= 0 for d in degree.values()),
            'invalid basis degree')
    require(all((degree[a] == 0) == (a in idem) for a in lower),
            'degree-zero basis is not the idempotent basis')
    require(all(corners[a] == (a, a) for a in idem), 'idempotent corner')
    table: dict[tuple[str, str], Vector] = {}
    for i in idem:
        for a in lower:
            if corners[a][0] == i:
                table[i, a] = unit(a)
            if corners[a][1] == i:
                table[a, i] = unit(a)
    for row in data['products']:
        inputs = tuple(row['inputs'])
        require(len(inputs) == 2 and set(inputs) <= set(lower), 'product inputs')
        require(inputs not in table, 'duplicate product or idempotent overwrite')
        value = {}
        for v, exponents in row['output'].items():
            require(v in lower, 'unknown product output')
            require(exponents and all(type(x) is int and x >= 0 for x in exponents)
                    and len(set(exponents)) == len(exponents), 'product polynomial')
            value[v] = frozenset((x, 0) for x in exponents)
        require(bool(value), 'explicit zero product')
        table[inputs] = value
    # (a phi)(c)=phi(ca), (phi a)(c)=phi(ac), DC*DC=0.
    # Calculate by evaluation, retaining both orientation choices explicitly.
    for a, b, c in product(lower, repeat=3):
        left_coefficient = table.get((c, a), {}).get(b, ZERO)
        right_coefficient = table.get((a, c), {}).get(b, ZERO)
        if left_coefficient:
            table.setdefault((a, b.upper()), {})[c.upper()] = left_coefficient
        if right_coefficient:
            table.setdefault((b.upper(), a), {})[c.upper()] = right_coefficient
    upper = tuple(a.upper() for a in lower)
    dual = {a: a.upper() for a in lower} | {a.upper(): a for a in lower}
    weight = {a: 0 for a in lower} | {a: 1 for a in upper}
    top_degree = max(degree.values()) + 1
    for a in lower:
        corners[a.upper()] = tuple(reversed(corners[a]))
        degree[a.upper()] = top_degree - degree[a]
    alg = Algebra(lower + upper, idem, corners, degree, dual, weight, table)
    support = frozenset(data['z_support'])
    require(len(support) == len(data['z_support']) and support <= set(alg.radical),
            'invalid z support')
    p: Cochain = {}
    for row in data['cochain']:
        inputs = tuple(row['inputs'])
        output, q_degree = row['output'], row['q_degree']
        require(len(inputs) == 3 and set(inputs) <= set(alg.radical),
                'cochain must have three radical inputs')
        require(output in alg.basis and inputs not in p, 'duplicate or invalid cochain')
        require(type(q_degree) is int and q_degree >= 0, 'invalid q degree')
        a, b, c = inputs
        require(corners[a][1] == corners[b][0] and corners[b][1] == corners[c][0]
                and corners[output] == (corners[a][0], corners[c][1]),
                'cochain endpoint mismatch')
        require(sum(weight[x] for x in inputs) == weight[output] + 1,
                'cochain weight mismatch')
        p[inputs] = {output: monomial(q_degree)}
    return alg, p, support


def check_algebra(alg: Algebra) -> int:
    """Complete associativity and trace-dual checks, plus radical/grading closure."""
    for (a, b), v in alg.table.items():
        for x in v:
            require(alg.corners[a][1] == alg.corners[b][0]
                    and alg.corners[x] == (alg.corners[a][0], alg.corners[b][1]),
                    'product endpoint mismatch')
            require(alg.degree[x] == alg.degree[a] + alg.degree[b],
                    'product degree mismatch')
    count = 0
    for a, b, c in product(alg.basis, repeat=3):
        residual = sum_vectors(alg.multiply(alg.table.get((a, b), {}), unit(c)),
                               alg.multiply(unit(a), alg.table.get((b, c), {})))
        if residual:
            raise IdentityFailure('associativity', (a, b, c), residual)
        count += 1
    # lambda picks the dual-idempotent coefficients; lambda(a b*) = delta_ab.
    for a, b in product(alg.basis, repeat=2):
        value = alg.table.get((a, alg.dual[b]), {})
        trace = ZERO
        for i in alg.idempotents:
            trace = add(trace, value.get(alg.dual[i], ZERO))
        residual = add(trace, ONE if a == b else ZERO)
        if residual:
            raise IdentityFailure('trace duality', (a, b), {'scalar': residual})
    return count


def insert_product(p: Cochain, args: tuple[str, str, str], slot: int,
                   value: Vector) -> Vector:
    result: Vector = {}
    for x, coefficient in value.items():
        inputs = args[:slot] + (x,) + args[slot + 1:]
        for v, cv in p.get(inputs, {}).items():
            accumulate(result, v, mul(coefficient, cv))
    return result


def check_cocycle(alg: Algebra, p: Cochain) -> tuple[int, int]:
    count = composable = 0
    for a, b, c, d in product(alg.radical, repeat=4):
        # a p(b,c,d) + p(ab,c,d) + p(a,bc,d) + p(a,b,cd) + p(a,b,c)d.
        residual = sum_vectors(
            alg.multiply(unit(a), p.get((b, c, d), {})),
            insert_product(p, (a, c, d), 0, alg.table.get((a, b), {})),
            insert_product(p, (a, b, d), 1, alg.table.get((b, c), {})),
            insert_product(p, (a, b, c), 2, alg.table.get((c, d), {})),
            alg.multiply(p.get((a, b, c), {}), unit(d)))
        if residual:
            raise IdentityFailure('cocycle', (a, b, c, d), residual)
        count += 1
        composable += (alg.corners[a][1] == alg.corners[b][0]
                       and alg.corners[b][1] == alg.corners[c][0]
                       and alg.corners[c][1] == alg.corners[d][0])
    return count, composable


def check_boundary(alg: Algebra, p: Cochain, support: frozenset[str],
                   twist: bool = True) -> int:
    def z(value: Vector) -> Vector:
        return scale({a: c for a, c in value.items() if a in support}, mul(Q, H))

    count = 0
    for a, b in product(alg.radical, repeat=2):
        left: Vector = {}
        for w in alg.radical:
            # Directly compute h_H(w), rather than the source's split recurrence.
            pw = scale(p.get((a, b, w), {}), monomial(0, alg.weight[w])
                       if twist else ONE)
            left = sum_vectors(left, alg.multiply(pw, unit(alg.dual[w])))
        right = sum_vectors(
            alg.multiply(unit(a), z(unit(b))),
            z(alg.table.get((a, b), {})),
            alg.multiply(z(unit(a)), scale(unit(b), monomial(0, -alg.weight[b]))))
        residual = sum_vectors(left, right)
        if residual:
            raise IdentityFailure('twisted boundary', (a, b), residual)
        count += 1
    return count


def cycle(alg: Algebra, p: Cochain) -> tuple[dict, Vector]:
    boundary: dict = {}
    value: Vector = {}
    for word, coefficient in [(('t', 'x', 'J'), monomial(2)),
                              (('t', 'y', 'J'), ONE)]:
        require(alg.corners[word[0]][0] == 'f'
                and alg.corners[word[-1]][1] == 'f', 'cycle simple endpoints')
        # Outer radical actions on either simple vanish; only two internal faces.
        for i in range(2):
            for x, cx in alg.table.get(word[i:i + 2], {}).items():
                new_word = word[:i] + (x,) + word[i + 2:]
                accumulate(boundary, new_word, mul(coefficient, cx))
        value = sum_vectors(value, scale(p.get(word, {}), coefficient))
    return boundary, value


def verify(alg: Algebra, p: Cochain, support: frozenset[str],
           twist: bool = True) -> dict:
    triples = check_algebra(alg)
    quadruples, composable = check_cocycle(alg, p)
    pairs = check_boundary(alg, p, support, twist)
    boundary, value = cycle(alg, p)
    if boundary:
        raise IdentityFailure('bar cycle', ('zeta',), boundary)
    residual = sum_vectors(value, {'f': monomial(3)})
    if residual:
        raise IdentityFailure('cycle evaluation', ('zeta',), residual)
    return {'associativity_triples': triples, 'trace_duality_pairs': len(alg.basis)**2,
            'cochain_entries': len(p), 'cocycle_quadruples': quadruples,
            'composable_quadruples': composable, 'boundary_pairs': pairs,
            'cycle_boundary': {}, 'cycle_evaluation': encode(value),
            'coefficient_ring': 'F_2[q,H,H^-1]', 'result': 'holds'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, default=Path(__file__).with_name('data.json'))
    parser.add_argument('--mutate', choices=['cochain', 'twist', 'dual'])
    args = parser.parse_args()
    try:
        alg, p, support = load_data(json.loads(args.data.read_text()))
        if args.mutate == 'cochain':
            p['t', 'y', 'J'] = {'f': monomial(2)}
        if args.mutate == 'dual':
            alg.table['x', 'J'] = {'T': Q}
        result = verify(alg, p, support, twist=args.mutate != 'twist')
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f'RESULT: FAIL: {error}')
        return 1
    print(json.dumps(result, sort_keys=True, indent=2))
    print('RESULT: holds — exact finite cocycle and twisted boundary identities; '
          'full counterexample theorem not checked')
    return 0


if __name__ == '__main__':
    sys.exit(main())
