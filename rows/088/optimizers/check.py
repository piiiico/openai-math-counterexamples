"""Finite certificate for PROOF.md; the written induction supplies all-n scope.

Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
Inherited analytic cap19 and ratio lemma: sources.json, predecessor/PROOF.md.
"""
import argparse
import copy
from fractions import Fraction
from functools import lru_cache
import hashlib
import json
from math import factorial
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


@lru_cache(maxsize=None)
def c(d: int) -> Fraction:
    require(type(d) is int and d >= 2, 'invalid simplex dimension')
    return Fraction((d + 1) * d**d, factorial(d))


def formula(n: int) -> tuple[tuple[int, int], ...]:
    """Sparse eventual optimizer; no list allocation proportional to n."""
    require(type(n) is int and n >= 100, 'formula requires integer n>=100')
    q, r = divmod(n, 13)
    counts = ((13, q-r), (14, r)) if r <= 8 else ((12, 13-r), (13, q+r-12))
    require(all(count >= 0 for _, count in counts), 'negative multiplicity')
    return tuple((d, count) for d, count in counts if count)


def make_certificate(cutoff: int = 100) -> dict:
    require(type(cutoff) is int and cutoff >= 3, 'invalid cutoff')
    values = {0: Fraction(1)}
    witnesses = {0: ((),)}
    states = [{'n': 0, 'value': [1, 1], 'witnesses': [[]], 'last_parts': []}]
    for n in range(2, cutoff + 32):
        candidates = [(c(d) * values[n-d], d) for d in range(2, 20) if n-d in values]
        best = max(value for value, _ in candidates)
        last = [d for value, d in candidates if value == best]
        ws = tuple(sorted({tuple(sorted((d,) + w)) for d in last for w in witnesses[n-d]}))
        values[n], witnesses[n] = best, ws
        states.append({'n': n, 'value': [best.numerator, best.denominator],
                       'witnesses': [list(w) for w in ws], 'last_parts': last})
    return {'schema_version': 1, 'minimum_factor': 2, 'maximum_factor': 19,
            'period': 13, 'cutoff': cutoff, 'states': states}


def balanced_oracle(n: int) -> tuple[Fraction, tuple[tuple[int, ...], ...]]:
    """Different algorithm: optimize all balanced fixed-cardinality partitions."""
    require(type(n) is int and n >= 2, 'invalid oracle dimension')
    best = Fraction(0)
    winners = []
    for k in range(1, n//2 + 1):
        a, b = divmod(n, k)
        value = c(a)**(k-b) * (c(a+1)**b if b else 1)
        if value >= best:
            witness = (a,) * (k-b) + (a+1,) * b
            if value > best:
                best, winners = value, []
            winners.append(witness)
    return best, tuple(sorted(winners))


def verify(cert: dict) -> dict:
    require(cert.get('schema_version') == 1 and cert.get('minimum_factor') == 2
            and cert.get('maximum_factor') == 19 and cert.get('period') == 13,
            'unsupported parameters')
    start = cert.get('cutoff')
    require(type(start) is int and start >= 3, 'invalid cutoff')
    states = cert.get('states', [])
    require([s.get('n') for s in states] == [0] + list(range(2, start+32)),
            'state domain incomplete or unordered')
    require(states[0] == {'n': 0, 'value': [1, 1], 'witnesses': [[]], 'last_parts': []},
            'empty base state differs')
    values, witnesses = {0: Fraction(1)}, {0: ((),)}
    comparisons = 0
    for s in states[1:]:
        n = s['n']
        raw = s['value']
        require(len(raw) == 2 and all(type(x) is int and x > 0 for x in raw),
                'invalid positive rational')
        value = Fraction(*raw)
        require(raw == [value.numerator, value.denominator], 'noncanonical rational')
        candidates = {d: c(d) * values[n-d] for d in range(2, 20) if n-d in values}
        comparisons += len(candidates)
        require(value == max(candidates.values()), f'incorrect maximum at {n}')
        last = sorted(d for d, product in candidates.items() if product == value)
        require(s['last_parts'] == last, f'incomplete maximizing competitors at {n}')
        expected = tuple(sorted({tuple(sorted((d,) + w)) for d in last for w in witnesses[n-d]}))
        require(s['witnesses'] == [list(w) for w in expected], f'incomplete witnesses at {n}')
        require(len(expected) == 1, f'nonunique optimum at {n}')
        values[n], witnesses[n] = value, expected
    for n in range(start, start+19):
        require(values[n+13] == c(13)*values[n], f'period value fails at {n}')
        appended = tuple(sorted(tuple(sorted((13,) + w)) for w in witnesses[n]))
        require(witnesses[n+13] == appended, f'period witnesses fail at {n}')
    require(values[start+12] != c(13)*values[start-1], 'cutoff is not minimal')
    for n in range(max(start, 100), start+32):
        expanded = tuple(d for d, count in formula(n) for _ in range(count))
        require(witnesses[n] == (expanded,), f'residue formula differs at {n}')
    boundary = values[start+12]/(c(13)*values[start-1])
    return {'cutoff': start, 'period': 13, 'states': len(states),
            'candidate_comparisons': comparisons, 'window_checks': 19,
            'boundary_ratio': [boundary.numerator, boundary.denominator],
            'base_witnesses': {str(n): list(witnesses[n][0]) for n in range(start, start+13)}}


def mutate(cert: dict, control: str) -> dict:
    bad = copy.deepcopy(cert)
    if control == 'early_cutoff':
        bad['cutoff'] = 99
        bad['states'] = bad['states'][:-1]
    elif control == 'wrong_witness':
        next(s for s in bad['states'] if s['n'] == 112)['witnesses'] = [[13]*8 + [8]]
    elif control == 'omit_competitor':
        next(s for s in bad['states'] if s['n'] == 100)['last_parts'].pop()
    elif control == 'wrong_value':
        next(s for s in bad['states'] if s['n'] == 26)['value'][0] += 1
    else:
        raise ValueError('unknown control')
    return bad


def check_sources() -> int:
    sources = json.loads((ROOT/'sources.json').read_text())
    for f in sources['files']:
        require(hashlib.sha256((ROOT/f['local']).read_bytes()).hexdigest() == f['sha256'],
                f'source hash differs: {f["local"]}')
    return len(sources['files'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=ROOT/'certificate.json')
    parser.add_argument('--control', choices=['early_cutoff', 'wrong_witness', 'omit_competitor', 'wrong_value'])
    args = parser.parse_args()
    cert = json.loads(args.certificate.read_text())
    if args.control:
        cert = mutate(cert, args.control)
    result = verify(cert)
    for s in cert['states'][1:]:
        value, ws = balanced_oracle(s['n'])
        require(value == Fraction(*s['value']) and [list(w) for w in ws] == s['witnesses'],
                f'balanced oracle differs at {s["n"]}')
    result['source_files'] = check_sources()
    result['balanced_oracle_dimensions'] = len(cert['states'])-1
    print(json.dumps(result, sort_keys=True, indent=2))
    print('RESULT: exact states through131 and 19-step window support the written cutoff100 and residue proof')


if __name__ == '__main__':
    main()
