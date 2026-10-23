"""Exact weighted-GCD verification of Family 059, Lemma seed:product.

openai/math fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, manuscript
Ambiently-homeomorphic-isolated-hypersurfaces-of-multiplicities-two-and-three,
build/sections/seeds.tex:7-19. Exact source hashes are in source-pins.json.

Alexander Richard Towell; substantial OpenAI Codex assistance. MIT.
Credits: OpenAI's witness, authors' trial-division validation, Pico's sieve check.
This checks the explicit arithmetic witness, not the topological theorem.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import json
from math import gcd
from pathlib import Path
import sys

DIMENSION = 3**11
Powers = tuple[int, int]
Term = tuple[int, Powers]
ZERO: Powers = (0, 0)
CONTROLS = ('coefficient', 'wrong-ratio', 'reverse-sign', 'invalid-index', 'wrong-d')


class InvalidCertificate(ValueError):
    """The supplied evidence or a necessary identity failed."""


@dataclass(frozen=True)
class Reduction:
    residual: dict[int, Powers]
    input_terms: int
    combined_bases: int
    gcd_calls: int
    splits: int


@dataclass(frozen=True)
class Row:
    b: int
    e: int


@dataclass(frozen=True)
class Witness:
    rows: tuple[Row, ...]
    sum_e: int
    sum_abs_e: int
    max_abs_e_digits: int

    @property
    def support_size(self) -> int:
        return len(self.rows)


@dataclass(frozen=True)
class Verified:
    support_size: int
    sum_e: int
    sum_abs_e: int
    max_abs_e_digits: int
    reduction: Reduction


def add(left: Powers, right: Powers) -> Powers:
    return left[0] + right[0], left[1] + right[1]


def cancel(terms) -> Reduction:
    """Preserve both rational products while reducing to coprime integer bases.

    Stored bases are pairwise coprime. A colliding pending/stored pair is
    replaced by a/g, b/g and g with exponent pairs u, v and u+v. No powers
    of the input bases are evaluated. See PROOF.md for soundness/termination.
    """
    combined: dict[int, Powers] = {}
    count = 0
    for term in terms:
        if not isinstance(term, (tuple, list)) or len(term) != 2:
            raise InvalidCertificate('malformed term')
        base, powers = term
        if type(base) is not int or base < 1:
            raise InvalidCertificate('base must be a positive integer')
        if (not isinstance(powers, (tuple, list)) or len(powers) != 2
                or any(type(e) is not int for e in powers)):
            raise InvalidCertificate('two integer exponents required')
        count += 1
        if base != 1:
            combined[base] = add(combined.get(base, ZERO), tuple(powers))
    pending = [(base, powers) for base, powers in sorted(combined.items()) if powers != ZERO]
    initial_bases = len(pending)
    basis: dict[int, Powers] = {}
    calls = splits = 0
    while pending:
        n, v = pending.pop()
        if n == 1 or v == ZERO:
            continue
        for a, u in basis.items():
            calls += 1
            g = gcd(n, a)
            if g > 1:
                del basis[a]
                pending.extend(((a // g, u), (n // g, v), (g, add(u, v))))
                splits += 1
                break
        else:
            basis[n] = v
    return Reduction(dict(sorted(basis.items())), count, initial_bases, calls, splits)


def parse_relation(data) -> Witness:
    if not isinstance(data, dict):
        raise InvalidCertificate('relation document must be an object')
    if type(data.get('d')) is not int or data['d'] != DIMENSION:
        raise InvalidCertificate('wrong dimension: expected 3^11')
    raw_rows = data.get('relation')
    if not isinstance(raw_rows, list) or not raw_rows:
        raise InvalidCertificate('nonempty relation list required')
    rows = []
    seen = set()
    for raw in raw_rows:
        if not isinstance(raw, dict) or set(raw) != {'b', 'e'}:
            raise InvalidCertificate('each row must contain exactly b and e')
        b, value = raw['b'], raw['e']
        if type(b) is not int or not 0 < 2*b < DIMENSION or b % 3 == 0:
            raise InvalidCertificate('inadmissible index b')
        if b in seen:
            raise InvalidCertificate('duplicate index b')
        if type(value) is int:
            e = value
        elif isinstance(value, str):
            try:
                e = int(value)
            except ValueError as error:
                raise InvalidCertificate('noninteger coefficient') from error
            if str(e) != value:
                raise InvalidCertificate('noncanonical integer coefficient')
        else:
            raise InvalidCertificate('coefficient must be an integer or decimal integer string')
        if e == 0:
            raise InvalidCertificate('support contains a zero coefficient')
        seen.add(b)
        rows.append(Row(b, e))
    rows.sort(key=lambda row: row.b)
    witness = Witness(tuple(rows), sum(row.e for row in rows),
                      sum(abs(row.e) for row in rows),
                      max(len(str(abs(row.e))) for row in rows))
    computed = {'sum_e': witness.sum_e, 'sum_abs_e': witness.sum_abs_e,
                'support_size': witness.support_size,
                'max_abs_e_digits': witness.max_abs_e_digits}
    for field, value in computed.items():
        if type(data.get(field)) is not int or data[field] != value:
            raise InvalidCertificate(f'wrong exact metadata: {field}')
    return witness


def product_terms(witness: Witness, *, wrong_ratio: bool = False) -> list[Term]:
    d = DIMENSION
    terms = []
    for row in witness.rows:
        b, e = row.b, row.e
        terms.extend(((d-b, (e, 0)), (b, (-e, 0)),
                      (2*d+b, (0, e)), (2*d-b, (0, e)),
                      (3*d-b, (0, e if wrong_ratio else -e)),
                      (d+b, (0, -e))))
    return terms


def verify_relation(data, *, wrong_ratio: bool = False) -> Verified:
    witness = parse_relation(data)
    if witness.sum_e <= 0:
        raise InvalidCertificate('coefficient sum must be positive')
    reduction = cancel(product_terms(witness, wrong_ratio=wrong_ratio))
    if reduction.residual:
        raise InvalidCertificate(f'product identities failed: {len(reduction.residual)} residual coprime bases')
    return Verified(witness.support_size, witness.sum_e, witness.sum_abs_e,
                    witness.max_abs_e_digits, reduction)


def verify_sources(root: Path) -> None:
    pins = json.loads((root / 'source-pins.json').read_text())
    for name, expected in pins['sha256'].items():
        actual = hashlib.sha256((root / 'source' / name).read_bytes()).hexdigest()
        if actual != expected:
            raise InvalidCertificate(f'source hash mismatch: {name}')


def mutate(data, name):
    """Keep metadata consistent so arithmetic controls exercise the identities."""
    data = deepcopy(data)
    if name == 'coefficient':
        data['relation'][0]['e'] = str(int(data['relation'][0]['e']) + 1)
    elif name == 'reverse-sign':
        for row in data['relation']:
            row['e'] = str(-int(row['e']))
    elif name == 'invalid-index':
        data['relation'][0]['b'] = 3
    elif name == 'wrong-d':
        data['d'] += 1
    exponents = [int(row['e']) for row in data['relation']]
    data.update(sum_e=sum(exponents), sum_abs_e=sum(map(abs, exponents)),
                support_size=len(exponents),
                max_abs_e_digits=max(len(str(abs(e))) for e in exponents))
    return data


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--negative-control', choices=CONTROLS)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    try:
        verify_sources(root)
        data = json.loads((root / 'source/explicit-relation.json').read_text())
        if args.negative_control:
            data = mutate(data, args.negative_control)
        result = verify_relation(data, wrong_ratio=args.negative_control == 'wrong-ratio')
        print(f'd = {DIMENSION}; support = {result.support_size}; max coefficient digits = {result.max_abs_e_digits}')
        print(f'E = {result.sum_e} > 0')
        print(f'sum |e_b| = {result.sum_abs_e}')
        r = result.reduction
        print(f'input terms = {r.input_terms}; combined nonzero bases = {r.combined_bases}')
        print(f'GCD calls = {r.gcd_calls}; splits = {r.splits}; residual bases = {len(r.residual)}')
        print('RESULT: holds -- both exact rational products are 1; all indices admissible; E > 0')
        return 0
    except (InvalidCertificate, OSError, ValueError, KeyError) as error:
        print(f'RESULT: fails -- {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
