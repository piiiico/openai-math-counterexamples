"""Independent AI-review oracle for Family 199 parameter strata.

Reproduces the review's 30-parameter, 526-degree finite replay. Matrices are
derived from algebra.json and restricted to F2; all rank calculations use
binary XOR elimination, with no finite-field inverse and no check.py import.
This verifies finite dimensions and displayed quotient representatives, not
the all-degree theorem. Substantial OpenAI Codex assistance; author credit
for the contribution remains Alexander Richard Towell.

Run: python family199_parameters_independent_oracle.py /path/to/algebra.json
"""
import json
from pathlib import Path
import sys


def require(condition, context):
    if not condition:
        raise RuntimeError(context)


def field_mul(a, b, modulus):
    value = 0
    while b:
        if b & 1:
            value ^= a
        b >>= 1
        a <<= 1
    while value.bit_length() >= modulus.bit_length():
        value ^= modulus << (value.bit_length() - modulus.bit_length())
    return value


def field_pow(q, n, modulus):
    value = 1
    for _ in range(n):
        value = field_mul(value, q, modulus)
    return value


def rank(columns):
    pivots = {}
    for value in columns:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def apply(columns, vector):
    result = 0
    for i, column in enumerate(columns):
        if (vector >> i) & 1:
            result ^= column
    return result


def maps(data, modulus, q):
    names = [record['name'] for record in data['basis']]
    info = {record['name']: record for record in data['basis']}
    idempotents = set(data['idempotents'])
    degree = modulus.bit_length() - 1
    table = {}
    for a in names:
        for b in names:
            if a in idempotents and info[b]['left'] == a:
                table[a, b] = {b: 1}
            elif b in idempotents and info[a]['right'] == b:
                table[a, b] = {a: 1}
    for product in data['products']:
        output = {}
        for c, exponents in product['output'].items():
            value = 0
            for exponent in exponents:
                value ^= field_pow(q, exponent, modulus)
            output[c] = value
        table[tuple(product['inputs'])] = output

    def matrix(domain, codomain, factor, left=False):
        columns = []
        for a in domain:
            for i in range(degree):
                values = {}
                for b, coefficient in factor.items():
                    pair = (b, a) if left else (a, b)
                    for c, value in table.get(pair, {}).items():
                        scaled = field_mul(field_mul(1 << i, coefficient, modulus), value, modulus)
                        values[c] = values.get(c, 0) ^ scaled
                require(all(c in codomain or value == 0 for c, value in values.items()),
                        'product outside codomain')
                columns.append(sum(values.get(c, 0) << (degree * j)
                                   for j, c in enumerate(codomain)))
        return columns

    ce = [a for a in names if info[a]['right'] == 'e']
    cf = [a for a in names if info[a]['right'] == 'f']
    ec = [a for a in names if info[a]['left'] == 'e']
    fc = [a for a in names if info[a]['left'] == 'f']

    def ell(i):
        return {'x': 1, 'y': field_pow(q, i, modulus)}

    def chain(n):
        if n == 0:
            return [(1 << i) if a == 'f' else 0 for a in cf for i in range(degree)]
        if n == 1:
            return matrix(ce, cf, {'u': 1})
        return matrix(ce, ce, ell(n - 2))

    def cochain(n):
        if n == 0:
            return matrix(fc, ec, {'u': 1}, True)
        return matrix(ec, ec, ell(n - 1), True)

    def representatives(basis, letters):
        return [(1 << i) << (degree * basis.index(a))
                for a in letters for i in range(degree)]

    return degree, ce, cf, ec, fc, chain, cochain, representatives


def check_quotient(degree, outgoing, incoming, representatives, label):
    require(all(apply(outgoing, column) == 0 for column in incoming), (label, 'composition'))
    require(all(apply(outgoing, column) == 0 for column in representatives), (label, 'cycles'))
    require(len(outgoing) - rank(outgoing) - rank(incoming) == len(representatives),
            (label, 'quotient dimension'))
    require(rank(incoming + representatives) == rank(incoming) + len(representatives),
            (label, 'independence modulo boundaries'))
    require(len(representatives) % degree == 0, (label, 'scalar restriction'))


def run(data):
    cases = degree_cases = quotients = 0
    for modulus in (0b11, 0b111, 0b1011, 0b10011):
        degree = modulus.bit_length() - 1
        for q in range(1 << degree):
            order = 0
            if q:
                order = next(d for d in range(1, 1 << degree)
                             if field_pow(q, d, modulus) == 1)
            limit = 2 * max(order, 3) + 2
            degree, ce, cf, ec, fc, chain, cochain, reps = maps(data, modulus, q)
            for n in range(limit + 1):
                if n == 0:
                    letters = ['n'] if q == 1 else []
                elif n == 1:
                    letters = ['t', 'j'] if q == 1 else []
                else:
                    letters = (['t'] if q and n % order == 0 else [])
                    letters += ['j'] if q and (n + 1) % order == 0 else []
                representatives = reps(cf if n == 0 else ce, letters)
                check_quotient(degree, chain(n), chain(n + 1), representatives,
                               (modulus, q, n, 'chain'))
                if n < 2:
                    letters = []
                elif not q:
                    letters = ['x', 'v'] if n == 2 else ['y', 'z']
                else:
                    letters = ['u'] if (n - 1) % order == 0 else []
                    letters += ['v'] if (n - 2) % order == 0 else []
                representatives = reps(fc if n == 0 else ec, letters)
                incoming = [] if n == 0 else cochain(n - 1)
                check_quotient(degree, cochain(n), incoming, representatives,
                               (modulus, q, n, 'dual'))
                degree_cases += 1
                quotients += 2
            cases += 1
    return {'field_sizes': [2, 4, 8, 16], 'parameter_cases': cases,
            'degree_cases': degree_cases, 'quotients_and_representative_bases_checked': quotients,
            'method': 'restriction of scalars to F2; independent XOR-only binary elimination; no field inversion'}


if __name__ == '__main__':
    data_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('algebra.json')
    print(json.dumps(run(json.loads(data_path.read_text())), sort_keys=True))
