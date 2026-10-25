"""Separate AI review replay: unrestricted integer arithmetic, no checker imports.

Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
Finite corroboration only; PROOF.md supplies the all-dimensions induction.
"""
from math import comb, factorial, gcd
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


cert = json.loads((ROOT / 'certificate.json').read_text())
require((cert['minimum_factor'], cert['maximum_factor'], cert['period'],
         cert['cutoff']) == (2, 19, 13, 100), 'unexpected theorem parameters')
require([s['n'] for s in cert['states']] == [0] + list(range(2, 132)),
        'incorrect state domain')
scaled = {0: 1}
witnesses = {0: {()}}
last_parts = {0: []}
count = 0
for n in range(2, 132):
    best = 0
    winners = set()
    last = []
    for d in range(2, n + 1):
        if n - d not in scaled:
            continue
        count += 1
        candidate = comb(n, d) * (d + 1) * d**d * scaled[n - d]
        if candidate > best:
            best = candidate
            winners = set()
            last = []
        if candidate == best:
            last.append(d)
            winners.update(tuple(sorted(p + (d,))) for p in witnesses[n - d])
    scaled[n], witnesses[n], last_parts[n] = best, winners, last
for s in cert['states']:
    n = s['n']
    numerator, denominator = s['value']
    require(denominator > 0 and numerator * factorial(n) == denominator * scaled[n],
            f'value at {n}')
    require(s['witnesses'] == [list(p) for p in sorted(witnesses[n])],
            f'complete witnesses at {n}')
    require(s['last_parts'] == last_parts[n],
            f'complete maximizing competitors at {n}')
    require(len(witnesses[n]) == 1, f'nonunique optimum at {n}')


def comparison(n):
    left = scaled[n + 13] * factorial(n) * factorial(13)
    right = scaled[n] * 14 * 13**13 * factorial(n + 13)
    return left, right


for n in range(100, 119):
    left, right = comparison(n)
    require(left == right, f'value recurrence at {n}')
    require(witnesses[n + 13] == {tuple(sorted(p + (13,))) for p in witnesses[n]},
            f'witness recurrence at {n}')
left, right = comparison(99)
require(left > right, 'strict cutoff boundary')
g = gcd(left, right)
for n in range(100, 132):
    q, r = divmod(n, 13)
    p = ((13,) * (q - r) + (14,) * r if r <= 8
         else (12,) * (13 - r) + (13,) * (q + r - 12))
    require(sum(p) == n and witnesses[n] == {p}, f'residue formula at {n}')
print(json.dumps({'states': len(scaled), 'unrestricted_candidates': count,
                  'window_checks': 19, 'boundary_ratio': [left // g, right // g],
                  'complete_witness_sets_match': True}, sort_keys=True))
print('RESULT: unrestricted integer recurrence corroborates every finite certificate state and the induction window')
