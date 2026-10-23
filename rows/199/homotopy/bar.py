"""Direct sparse bar-tensor replay of Family199 Lemma lift:G.

Alexander Richard Towell; substantial OpenAI Codex assistance.
Source pin and inherited arithmetic are recorded in sources.json.
This program expands pB and dG+Gd separately, never their reduced formula.
"""
from __future__ import annotations

import argparse
from enum import Enum
from itertools import product
import json
from pathlib import Path
import sys

from dependency.check import (ONE, IdentityFailure, accumulate,
                              load_data, monomial, mul)

Tensor = dict[tuple[str, ...], frozenset[tuple[int, int]]]


class Homotopy(Enum):
    CORRECT = 'correct'
    OMIT_INVERSE_TWIST = 'omit-inverse-twist'
    OMIT_H = 'omit-H'
    DROP_U = 'drop-u'
    ZERO_G1 = 'zero-G1'


def add_tensors(*tensors: Tensor) -> Tensor:
    out: Tensor = {}
    for tensor in tensors:
        for word, coefficient in tensor.items():
            accumulate(out, word, coefficient)
    return out


class Bar:
    def __init__(self, algebra, cochain, support, mode=Homotopy.CORRECT):
        self.alg, self.cochain, self.support = algebra, cochain, support
        self.mode = mode

    @classmethod
    def load(cls, mode=Homotopy.CORRECT):
        data = json.loads((Path(__file__).parent / 'dependency/data.json').read_text())
        return cls(*load_data(data), mode)

    def generators(self, degree: int):
        if degree == 0:
            for vertex in self.alg.idempotents:
                yield {(vertex, vertex): ONE}
            return
        for bars in product(self.alg.radical, repeat=degree):
            if all(self.alg.corners[a][1] == self.alg.corners[b][0]
                   for a, b in zip(bars, bars[1:])):
                yield {(self.alg.corners[bars[0]][0], *bars,
                        self.alg.corners[bars[-1]][1]): ONE}

    def d(self, tensor: Tensor) -> Tensor:
        out: Tensor = {}
        for word, coefficient in tensor.items():
            if len(word) <= 2:  # Unaugmented P_0 -> 0.
                continue
            for position in range(len(word) - 1):
                for value, factor in self.alg.table.get(word[position:position+2], {}).items():
                    new = word[:position] + (value,) + word[position+2:]
                    accumulate(out, new, mul(coefficient, factor))
        return out

    def g(self, tensor: Tensor) -> Tensor:
        out: Tensor = {}
        for word, coefficient in tensor.items():
            if len(word) <= 2 or (self.mode is Homotopy.ZERO_G1 and len(word) == 3):
                continue
            last, terminal = word[-2:]
            if last not in self.support or (self.mode is Homotopy.DROP_U and last == 'u'):
                continue
            h_degree = 0 if self.mode is Homotopy.OMIT_H else 1
            if self.mode is not Homotopy.OMIT_INVERSE_TWIST:
                h_degree -= self.alg.weight[terminal]
            coefficient = mul(coefficient, monomial(1, h_degree))
            for value, factor in self.alg.table.get((last, terminal), {}).items():
                accumulate(out, word[:-2] + (value,), mul(coefficient, factor))
        return out

    def b(self, tensor: Tensor) -> Tensor:
        out: Tensor = {}
        for word, coefficient in tensor.items():
            terminal = word[-1]
            for w in self.alg.radical:
                if self.alg.corners[w][0] != self.alg.corners[terminal][0]:
                    continue
                coefficient_w = mul(coefficient, monomial(
                    h=self.alg.weight[w] - self.alg.weight[terminal]))
                for value, factor in self.alg.table.get((self.alg.dual[w], terminal), {}).items():
                    accumulate(out, word[:-1] + (w, value), mul(coefficient_w, factor))
        return out

    def p(self, tensor: Tensor) -> Tensor:
        out: Tensor = {}
        for word, coefficient in tensor.items():
            if len(word) < 5:
                continue
            for value, factor in self.cochain.get(word[-4:-1], {}).items():
                for terminal, product_factor in self.alg.table.get((value, word[-1]), {}).items():
                    accumulate(out, word[:-4] + (terminal,),
                               mul(coefficient, mul(factor, product_factor)))
        return out

    def left(self, letter: str, tensor: Tensor) -> Tensor:
        out: Tensor = {}
        for word, coefficient in tensor.items():
            for value, factor in self.alg.table.get((letter, word[0]), {}).items():
                accumulate(out, (value,) + word[1:], mul(coefficient, factor))
        return out

    def right(self, tensor: Tensor, letter: str, twisted: bool = False) -> Tensor:
        out: Tensor = {}
        for word, coefficient in tensor.items():
            coefficient = mul(coefficient, monomial(h=self.alg.weight[letter] if twisted else 0))
            for value, factor in self.alg.table.get((word[-1], letter), {}).items():
                accumulate(out, word[:-1] + (value,), mul(coefficient, factor))
        return out

    def residual(self, tensor: Tensor) -> Tensor:
        return add_tensors(self.p(self.b(tensor)), self.d(self.g(tensor)),
                           self.g(self.d(tensor)))

    def check_actions(self, max_degree: int) -> int:
        count = 0
        for degree in range(max_degree + 1):
            for tensor in self.generators(degree):
                for letter in self.alg.basis:
                    residuals = (
                        add_tensors(self.g(self.left(letter, tensor)),
                                    self.left(letter, self.g(tensor))),
                        add_tensors(self.g(self.right(tensor, letter, twisted=True)),
                                    self.right(self.g(tensor), letter)))
                    for side, residual in zip(('left', 'right'), residuals):
                        if residual:
                            raise IdentityFailure('G bimodule action',
                                                  (side, next(iter(tensor)), letter), residual)
                        count += 1
        return count

    def verify(self, max_degree: int = 4) -> dict:
        counts = []
        for degree in range(max_degree + 1):
            count = 0
            for tensor in self.generators(degree):
                residual = self.residual(tensor)
                if residual:
                    raise IdentityFailure('pB+dG+Gd', (degree, next(iter(tensor))), residual)
                count += 1
            counts.append(count)
        return {'generator_counts_by_degree': counts, 'total_generators': sum(counts),
                'G_bimodule_action_equalities': self.check_actions(min(max_degree, 2)),
                'coefficient_ring': 'F_2[q,H,H^-1]', 'result': 'holds'}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mutate', type=Homotopy, choices=list(Homotopy),
                        default=Homotopy.CORRECT)
    args = parser.parse_args()
    try:
        result = Bar.load(args.mutate).verify()
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f'RESULT: FAIL: {error}')
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    print('RESULT: holds — direct bar-tensor replay in degrees0..4; '
          'all-degree claim requires the written proof')
    return 0


if __name__ == '__main__':
    sys.exit(main())
