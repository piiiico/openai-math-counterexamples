"""Reviewer-provided exhaustive small oracle; standard-library exact rationals.

Alexander Richard Towell, with substantial OpenAI Codex assistance. MIT.
This finite implementation test is separate from the full Family 059 witness.
"""
from fractions import Fraction
from itertools import product
from math import gcd

import check


def oracle(terms):
    # Direct powers and rational normalization; no weighted splitting.
    answer = []
    for k in range(2):
        numerator = denominator = 1
        for base, powers in terms:
            exponent = powers[k]
            if exponent >= 0:
                numerator *= base**exponent
            else:
                denominator *= base**(-exponent)
        answer.append(Fraction(numerator, denominator))
    return tuple(answer)


def main():
    count = 0
    for bases in product(range(1, 11), repeat=3):
        for values in product((-1, 0, 1), repeat=6):
            terms = list(zip(bases, zip(values[:3], values[3:])))
            residual = check.cancel(terms).residual
            expected = oracle(terms)
            if expected != oracle(residual.items()) or (not residual) != (expected == (1, 1)):
                raise RuntimeError(('invariant or acceptance failure', terms, residual, expected))
            keys = list(residual)
            if any(gcd(a, b) != 1 for i, a in enumerate(keys) for b in keys[i+1:]):
                raise RuntimeError(('coprimality failure', terms, residual))
            if any(n <= 1 or v == (0, 0) for n, v in residual.items()):
                raise RuntimeError(('residual shape failure', terms, residual))
            count += 1
    print('Independent exhaustive direct-rational checks passed:', count)


if __name__ == '__main__':
    main()
