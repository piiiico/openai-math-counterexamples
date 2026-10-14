"""Exact sign-change root certificates and rigorous quadric determinant bounds."""

from dataclasses import dataclass
from itertools import combinations, combinations_with_replacement, islice
from math import comb

from flint import arb, arb_mat, ctx, fmpq, fmpq_poly

from .algebra import CertificationError, Representation


@dataclass(frozen=True)
class RootInterval:
    lower: fmpq
    upper: fmpq


@dataclass(frozen=True)
class DeterminantReport:
    checked: int
    total: int
    lower_bound: fmpq
    worst_subset: tuple[int, ...]

    @property
    def complete(self) -> bool:
        return self.checked == self.total


def propose_intervals(polynomial: fmpq_poly, bits: int) -> tuple[RootInterval, ...]:
    if bits < 32:
        raise CertificationError("root proposal precision must be at least 32 bits")
    scale = 2**bits
    intervals = []
    # These numerical roots are proposals only. Exact endpoint signs below are
    # the root certificate; correctness does not trust the numerical solver.
    with ctx.workprec(2 * bits):
        for root, multiplicity in polynomial.complex_roots():
            if multiplicity != 1 or not root.is_finite():
                raise CertificationError("root proposer did not return simple finite roots")
            center = root.real.mid().fmpq()
            grid = int((center * scale).floor())
            intervals.append(RootInterval(fmpq(grid - 1, scale), fmpq(grid + 2, scale)))
    intervals.sort(key=lambda interval: interval.lower)
    answer = tuple(intervals)
    verify_intervals(polynomial, answer)
    return answer


def verify_intervals(polynomial: fmpq_poly, intervals: tuple[RootInterval, ...]) -> None:
    if polynomial.degree() < 1 or len(intervals) != polynomial.degree():
        raise CertificationError("one disjoint sign-change interval per polynomial degree is required")
    previous_upper = None
    for interval in intervals:
        if interval.lower >= interval.upper:
            raise CertificationError("root interval endpoints must be strictly increasing")
        if previous_upper is not None and previous_upper >= interval.lower:
            raise CertificationError("root intervals must be ordered and disjoint")
        if polynomial(interval.lower) * polynomial(interval.upper) >= 0:
            raise CertificationError("exact rational endpoint signs do not prove a root")
        previous_upper = interval.upper


def enclose_points(representation: Representation, intervals: tuple[RootInterval, ...]) -> tuple:
    verify_intervals(representation.polynomial, intervals)
    points = []
    for interval in intervals:
        root = arb((interval.lower + interval.upper) / 2,
                   (interval.upper - interval.lower) / 2)
        coordinates = []
        for polynomial in representation.coordinates:
            value = arb(0)
            for coefficient in reversed(polynomial.coeffs()):
                value = value * root + arb(coefficient)
            coordinates.append(value)
        points.append((arb(1), *coordinates))
    return tuple(points)


def certify_determinants(points: tuple, limit: int | None = None) -> DeterminantReport:
    pairs = tuple(combinations_with_replacement(range(4), 2))
    size = len(pairs)
    if len(points) < size or any(len(point) != 4 for point in points):
        raise CertificationError("need at least ten projective four-coordinate points")
    if limit is not None and limit < 1:
        raise CertificationError("a prefix must contain at least one subset")
    rows = []
    for point in points:
        row = [point[i] * point[j] for i, j in pairs]
        norm = sum(value * value for value in row).sqrt()
        if not norm.is_finite() or norm.contains(0):
            raise CertificationError("quadratic row normalization is not certified")
        rows.append([value / norm for value in row])
    total = comb(len(points), size)
    subsets = combinations(range(len(points)), size)
    if limit is not None:
        subsets = islice(subsets, limit)
    checked = 0
    lower_bound = None
    worst_subset = ()
    for subset in subsets:
        determinant = arb_mat([rows[i] for i in subset]).det()
        if not determinant.is_finite() or determinant.contains(0):
            raise CertificationError(f"determinant not certified nonzero for subset {subset}")
        lower = determinant.abs_lower().fmpq()
        if lower_bound is None or lower < lower_bound:
            lower_bound, worst_subset = lower, subset
        checked += 1
    return DeterminantReport(checked, total, lower_bound, worst_subset)
