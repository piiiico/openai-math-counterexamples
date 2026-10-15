#!/usr/bin/env python3
"""Independent exact review of the Family 361 root-free finite selection.

Run from the repository root:
    python -m research.family361_spectral.review_check --method both

This file imports no code from the proposed certificate.  The recurrence
implementation visits every paired charge group in every individual degree.
The closed implementation instead uses Vandermonde and hockey-stick identities
to sum seven binomial terms, then binary-searches the admissible prefix.

The formulas reviewed are in counting.tex, links.tex, and finite-selection.tex
at openai/math commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb.  This is a
finite arithmetic review, not a review of the metric/transmission construction.
All numerical comparisons below use integers or fractions, without roots.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from fractions import Fraction
from math import comb
from pathlib import Path


K = 50000
EXPONENT_THRESHOLD = K * (K + 14)
DENOMINATOR = 101 * 99853
NUMERATOR_THRESHOLD = DENOMINATOR * EXPONENT_THRESHOLD
EXPECTED_SELECTED = 46785537904676899645365728857267392956181699200186010789105
EXPECTED_COMPARATOR = 46779709349146362239266126538609505511855492134986686636251
EXPECTED_SURPLUS = 5828555530537406099602318657887444326207065199324152854


def require(condition: bool, message: str) -> None:
    """Do not silently disable verification under Python's -O option."""
    if not condition:
        raise AssertionError(message)


def dimension(degree: int) -> int:
    return comb(degree + 15, 15) - (
        comb(degree + 13, 15) if degree >= 2 else 0
    )


def eigenvalue_numerator(degree: int, b: int) -> int:
    return 100000 * (101 * degree * (degree + 14) - (degree - 2 * b) ** 2)


def bidegree_dimension(degree: int, b: int) -> int:
    result = comb(b + 7, 7) * comb(degree - b + 7, 7)
    if b and degree - b:
        result -= comb(b + 6, 7) * comb(degree - b + 6, 7)
    return result


def paired_dimension(degree: int, b: int) -> int:
    return bidegree_dimension(degree, b) * (1 if 2 * b == degree else 2)


@dataclass(frozen=True)
class Selection:
    degree: int
    count: int
    slack: int
    boundary_b: int | None
    taken_at_boundary: int = 0
    boundary_multiplicity: int = 0
    next_vector_excess: int = 0


def closed_prefix(degree: int, groups: int) -> tuple[int, int]:
    """Real dimension and squared-charge sum of b = 0,...,groups-1.

    Vandermonde gives
      C(l-b+6,6) = sum_j (-1)^j C(l+6-j,6-j) C(b,j).
    Multiplication by C(b+6,6) changes C(b,j) to
      C(6+j,6) C(b+6,6+j).
    Summing over b uses the hockey-stick identity.  First and second b
    moments follow from b C(b+6,r) = (r+1) C(b+6,r+1)
    + (r-6) C(b+6,r).  No polynomial interpolation is used.
    """
    require(0 <= groups <= degree // 2 + 1, "prefix outside charge range")
    mass = first = second = 0
    for j in range(7):
        coefficient = (-1) ** j * comb(degree + 6 - j, 6 - j) * comb(6 + j, 6)
        x = comb(groups + 6, 7 + j)
        y = comb(groups + 6, 8 + j)
        z = comb(groups + 6, 9 + j)
        mass += coefficient * x
        first += coefficient * ((7 + j) * y + j * x)
        second += coefficient * (
            (7 + j) * (8 + j) * z + (7 + j) * (2 * j + 1) * y + j * j * x
        )
    charge = degree * degree * mass - 4 * degree * first + 4 * second
    mass *= degree + 7
    charge *= degree + 7
    require(mass % 7 == charge % 7 == 0, "nonintegral closed prefix")
    mass, charge = 2 * (mass // 7), 2 * (charge // 7)
    if degree % 2 == 0 and groups == degree // 2 + 1:
        # The middle bidegree is counted once; its squared charge is zero.
        mass -= bidegree_dimension(degree, degree // 2)
    return mass, charge


def residual(degree: int, count: int, charge: int) -> int:
    return (
        (100000 * 101 * degree * (degree + 14) - NUMERATOR_THRESHOLD) * count
        - 100000 * charge
    )


def select_closed(degree: int) -> Selection:
    groups = degree // 2 + 1
    count, charge = closed_prefix(degree, groups)
    require(count == dimension(degree), "closed dimension mismatch")
    require(15 * charge == degree * (degree + 14) * count, "charge moment mismatch")
    value = residual(degree, count, charge)
    if value < 0:
        return Selection(degree, count, -value, None)
    low, high = 1, groups
    require(residual(degree, *closed_prefix(degree, low)) < 0, "empty initial group")
    while high - low > 1:
        middle = (low + high) // 2
        if residual(degree, *closed_prefix(degree, middle)) < 0:
            low = middle
        else:
            high = middle
    count, charge = closed_prefix(degree, low)
    value = residual(degree, count, charge)
    step = eigenvalue_numerator(degree, low) - NUMERATOR_THRESHOLD
    require(value < 0 and step > 0, "invalid partial-group boundary")
    take = (-value - 1) // step
    multiplicity = paired_dimension(degree, low)
    require(0 <= take < multiplicity, "partial group outside eigenspace")
    value += take * step
    require(value < 0 <= value + step, "non-strict or non-maximal partial cut")
    return Selection(degree, count + take, -value, low, take, multiplicity, step)


def select_recurrence(degree: int) -> Selection:
    """Visit all paired groups, including groups after the selection ends."""
    count = value = total = 0
    h = comb(degree + 7, 7)
    result = None
    for b in range(degree // 2 + 1):
        multiplicity = h if 2 * b == degree else 2 * h
        total += multiplicity
        if result is None:
            step = eigenvalue_numerator(degree, b) - NUMERATOR_THRESHOLD
            if value + multiplicity * step < 0:
                count += multiplicity
                value += multiplicity * step
            else:
                require(count > 0 and value < 0 and step > 0, "bad recurrence boundary")
                take = (-value - 1) // step
                require(0 <= take < multiplicity, "bad recurrence partial count")
                count += take
                value += take * step
                require(value < 0 <= value + step, "bad recurrence strict margin")
                result = Selection(degree, count, -value, b, take, multiplicity, step)
        if b < degree // 2:
            dividend = h * (b + 7) * (degree - b)
            divisor = (b + 1) * (degree - b + 6)
            require(dividend % divisor == 0, "nonintegral multiplicity recurrence")
            h = dividend // divisor
    require(total == dimension(degree), "recurrence dimension mismatch")
    require(0 < count <= total and value < 0, "invalid recurrence selection")
    return result if result is not None else Selection(degree, count, -value, None)


def check_multiplicities() -> int:
    checked = 0
    degrees = list(range(65)) + [49963, 49964, 49979, 49980, 50000, 50212, 50213]
    for degree in degrees:
        total = charge = 0
        for b in range(degree + 1):
            h = bidegree_dimension(degree, b)
            product = (degree + 7) * comb(b + 6, 6) * comb(degree - b + 6, 6)
            require(product % 7 == 0 and product // 7 == h, "multiplicity formulas disagree")
            total += h
            charge += h * (2 * b - degree) ** 2
            checked += 1
        require(total == dimension(degree), "literal multiplicity sum mismatch")
        require(15 * charge == degree * (degree + 14) * total, "literal charge moment mismatch")
        if degree < 65:
            count = moment = 0
            for groups in range(degree // 2 + 2):
                require(closed_prefix(degree, groups) == (count, moment), "small prefix mismatch")
                if groups <= degree // 2:
                    multiplicity = paired_dimension(degree, groups)
                    count += multiplicity
                    moment += multiplicity * (degree - 2 * groups) ** 2
    return checked


def check_parameters() -> None:
    require(Fraction(1) - Fraction(1, 700) - Fraction(99853, 100000) == Fraction(29, 700000),
            "curvature endpoint mismatch")
    require(101 * 99853**15 < 100 * 100000**15, "radial scale not below one")
    require(Fraction(147, 2 * 99853) < Fraction(1, 1000), "logarithmic upper bound too large")
    require(5 < 2**4, "cutoff integral lower bound failed")
    # For every stated cutoff: I_chi >= 4*5^(-1/4) > 2 and sup <= 1.
    # Hence (-log a)/I_chi * sup < 1/2000 < 1/4.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("closed", "recurrence", "both"), default="both")
    parser.add_argument("--certificate", type=Path, help="also compare every field of an external certificate")
    args = parser.parse_args()
    check_parameters()
    multiplicity_checks = check_multiplicities()
    full_cutoff = 0
    while (full_cutoff + 1) * (full_cutoff + 15) * 100000 < 99853 * EXPONENT_THRESHOLD:
        full_cutoff += 1
    excluded_cutoff = 0
    while eigenvalue_numerator(excluded_cutoff, 0) < NUMERATOR_THRESHOLD:
        excluded_cutoff += 1
    require((full_cutoff, excluded_cutoff) == (49963, 50213), "unexpected degree cutoffs")
    selected = sum(dimension(degree) for degree in range(2, full_cutoff + 1))
    rows = []
    for degree in range(full_cutoff + 1, excluded_cutoff):
        if args.method == "recurrence":
            row = select_recurrence(degree)
        else:
            row = select_closed(degree)
            if args.method == "both":
                require(row == select_recurrence(degree), f"implementations differ at degree {degree}")
        rows.append(row)
        selected += row.count
    comparator = sum(dimension(degree) for degree in range(K + 1))
    require(comparator == comb(K + 15, 15) + comb(K + 14, 15), "comparator telescoping mismatch")
    require(selected == EXPECTED_SELECTED, "selected dimension changed")
    require(comparator == EXPECTED_COMPARATOR, "comparator changed")
    require(selected - comparator == EXPECTED_SURPLUS > 0, "surplus changed or nonpositive")
    partial = [row for row in rows if row.boundary_b is not None]
    require(len(rows) - len(partial) == 16 and len(partial) == 233, "full/partial counts changed")
    certificate_rows_compared = 0
    if args.certificate is not None:
        certificate = json.loads(args.certificate.read_text())
        require(len(certificate["degrees"]) == len(rows), "external certificate row count differs")
        for external, row in zip(certificate["degrees"], rows):
            expected = {
                "degree": row.degree,
                "full_groups": row.degree // 2 + 1 if row.boundary_b is None else row.boundary_b,
                "partial_take": row.taken_at_boundary,
                "count": row.count,
                "weighted_num": NUMERATOR_THRESHOLD * row.count - row.slack,
                "slack": row.slack,
            }
            require(external == expected, f"external certificate differs at degree {row.degree}")
            certificate_rows_compared += 1
        require(certificate["full_cutoff"] == full_cutoff, "external full cutoff differs")
        require(certificate["last_degree"] == excluded_cutoff - 1, "external last degree differs")
        require(certificate["selected"] == selected, "external selected total differs")
        require(certificate["comparator"] == comparator, "external comparator differs")
        require(certificate["surplus"] == selected - comparator, "external surplus differs")
    print(json.dumps({
        "method": args.method,
        "parameters": {"s": 8, "m": 15, "k": K, "q": "101/100", "alpha_squared": "99853/100000"},
        "fully_selected_by_worst_eigenvalue": [2, full_cutoff],
        "individually_checked": [full_cutoff + 1, excluded_cutoff - 1],
        "additional_full_degrees": len(rows) - len(partial),
        "partial_degrees": len(partial),
        "first_partial_degree": partial[0].degree,
        "omitted_low_degree_dimensions": dimension(0) + dimension(1),
        "multiplicity_formula_comparisons": multiplicity_checks,
        "certificate_rows_compared": certificate_rows_compared,
        "minimum_partial_integer_slack": min(row.slack for row in partial),
        "selected": selected,
        "comparator": comparator,
        "surplus": selected - comparator,
        "checks": "passed",
    }, indent=2))


if __name__ == "__main__":
    main()
