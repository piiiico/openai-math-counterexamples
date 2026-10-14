"""Check symbolic minors by an independent, division-free permutation expansion.

Run: python -m research.family272.independent_minor_check
The expansion uses Python integer coefficient dictionaries, without SymPy or
FLINT determinant routines. The checked target comes from ``maximal_minors``.
"""

import argparse
from collections import defaultdict
from itertools import combinations, permutations
from pathlib import Path

from .algebra import CertificationError, Polynomial, load_pencil, maximal_minors


def permutation_minors(matrices: tuple) -> tuple[Polynomial, ...]:
    """Expand all maximal minors of an affine pencil with exact integers."""
    row_count, column_count = len(matrices[0]), len(matrices[0][0])
    variable_count = len(matrices) - 1
    constant = (0,) * variable_count
    terms = tuple(tuple(int(k == j + 1) for j in range(variable_count))
                  for k in range(len(matrices)))
    answer = []
    for rows in combinations(range(row_count), column_count):
        result = defaultdict(int)
        for permutation in permutations(range(column_count)):
            inversions = sum(permutation[i] > permutation[j]
                             for i in range(column_count)
                             for j in range(i + 1, column_count))
            product = {constant: (-1) ** inversions}
            for i, column in enumerate(permutation):
                factors = {term: matrices[k][rows[i]][column]
                           for k, term in enumerate(terms)
                           if matrices[k][rows[i]][column]}
                expanded = defaultdict(int)
                for left, left_coefficient in product.items():
                    for right, right_coefficient in factors.items():
                        exponent = tuple(a + b for a, b in zip(left, right))
                        expanded[exponent] += left_coefficient * right_coefficient
                product = expanded
            for monomial, coefficient in product.items():
                result[monomial] += coefficient
        answer.append({m: c for m, c in result.items() if c})
    return tuple(answer)


def check(matrices: tuple, minors: tuple[Polynomial, ...]) -> None:
    """Raise if any supplied minor differs from its permutation expansion."""
    if permutation_minors(matrices) != minors:
        raise CertificationError("maximal minors differ from independent permutation expansion")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pencil", type=Path, default=Path(__file__).with_name("pencil.json"))
    matrices = load_pencil(parser.parse_args().pencil)
    minors = maximal_minors(matrices)
    check(matrices, minors)
    print(f"All {len(minors)} maximal minors match independent permutation expansion.")


if __name__ == "__main__":
    main()
