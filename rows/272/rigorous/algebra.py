"""Exact rational certificate generation and verification."""

from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path

from flint import fmpq_mat, fmpq_poly
from sympy import Matrix, Poly, symbols, zeros

Monomial = tuple[int, int, int]
Polynomial = dict[Monomial, int]


class CertificationError(ValueError):
    """A proof obligation failed or could not be certified."""


@dataclass(frozen=True)
class Representation:
    polynomial: fmpq_poly
    coordinates: tuple[fmpq_poly, fmpq_poly, fmpq_poly]


def load_pencil(path: Path) -> tuple:
    matrices = json.loads(path.read_text())["matrices"]
    if (len(matrices) != 4 or any(len(m) != 6 for m in matrices)
            or any(len(row) != 4 for m in matrices for row in m)
            or any(type(value) is not int for m in matrices for row in m for value in row)):
        raise CertificationError("expected four exact integer matrices of shape 6 by 4")
    return tuple(tuple(tuple(row) for row in matrix) for matrix in matrices)


def maximal_minors(matrices: tuple) -> tuple[Polynomial, ...]:
    variables = symbols("t1 t2 t3")
    pencil = sum((scalar * Matrix(matrix) for scalar, matrix in zip((1, *variables), matrices)), zeros(6, 4))
    return tuple(dict((monomial, int(coefficient)) for monomial, coefficient in
                      Poly(pencil.extract(rows, range(4)).det(method="domain-ge"), *variables).terms())
                 for rows in combinations(range(6), 4))


def monomials(max_degree: int) -> tuple[Monomial, ...]:
    return tuple((a, b, degree - a - b) for degree in range(max_degree + 1)
                 for a in range(degree + 1) for b in range(degree - a + 1))


def reduction_matrices(minors: tuple) -> tuple:
    low = monomials(3)
    high = tuple(m for m in monomials(4) if sum(m) == 4)
    return (fmpq_mat([[polynomial.get(m, 0) for m in high] for polynomial in minors]),
            fmpq_mat([[polynomial.get(m, 0) for m in low] for polynomial in minors]))


def generate_representation(minors: tuple) -> Representation:
    high_matrix, low_matrix = reduction_matrices(minors)
    if high_matrix.det() == 0:
        raise CertificationError("quartic coefficient matrix is singular")
    reductions = -high_matrix.solve(low_matrix)
    low = monomials(3)
    high = tuple(m for m in monomials(4) if sum(m) == 4)
    low_index = {m: i for i, m in enumerate(low)}
    high_index = {m: i for i, m in enumerate(high)}
    size = len(low)
    multiplication = fmpq_mat(size, size)
    for column, monomial in enumerate(low):
        shifted = (monomial[0] + 1, monomial[1], monomial[2])
        if sum(shifted) <= 3:
            multiplication[low_index[shifted], column] = 1
        else:
            for row in range(size):
                multiplication[row, column] = reductions[high_index[shifted], row]
    polynomial = multiplication.charpoly()
    vector = fmpq_mat([[int(i == low_index[(0, 0, 0)])] for i in range(size)])
    krylov = fmpq_mat(size, size)
    for column in range(size):
        for row in range(size):
            krylov[row, column] = vector[row, 0]
        vector = multiplication * vector
    targets = fmpq_mat([[int(m == (0, 1, 0)), int(m == (0, 0, 1))] for m in low])
    if krylov.det() == 0:
        raise CertificationError("t1 does not generate this candidate representation")
    coefficients = krylov.solve(targets)
    return Representation(polynomial, (fmpq_poly([0, 1]),
                          fmpq_poly([coefficients[i, 0] for i in range(size)]),
                          fmpq_poly([coefficients[i, 1] for i in range(size)])))


def verify_representation(minors: tuple, representation: Representation) -> None:
    high_matrix, _ = reduction_matrices(minors)
    if len(minors) != 15 or high_matrix.det() == 0:
        raise CertificationError("dimension bound requires fifteen minors and invertible H")
    polynomial = representation.polynomial
    coordinates = representation.coordinates
    if (polynomial.degree() != 20 or polynomial.leading_coefficient() != 1
            or len(coordinates) != 3 or coordinates[0] != fmpq_poly([0, 1])
            or any(c.degree() >= 20 for c in coordinates)):
        raise CertificationError("expected a monic degree-twenty representation with t1=z")
    powers = [[(coordinate**exponent) % polynomial for exponent in range(5)] for coordinate in coordinates]
    for index, minor in enumerate(minors):
        residual = fmpq_poly([])
        for monomial, coefficient in minor.items():
            term = fmpq_poly([coefficient])
            for variable, exponent in enumerate(monomial):
                term = (term * powers[variable][exponent]) % polynomial
            residual = (residual + term) % polynomial
        if not residual.is_zero():
            raise CertificationError(f"minor {index} is not zero in the proposed quotient")
