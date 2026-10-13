"""Failure controls for roots, singular quadrics, uncertainty and coverage."""

from flint import arb, ctx, fmpq, fmpq_poly
import pytest

from .algebra import CertificationError, Representation, monomials
from .enclosures import (RootInterval, certify_determinants, enclose_points,
                         propose_intervals, verify_intervals)


def test_exact_sign_changes_certify_all_real_roots():
    polynomial = fmpq_poly([-2, 0, 1])
    intervals = propose_intervals(polynomial, 64)
    assert len(intervals) == 2
    assert intervals[0].upper < 0 < intervals[1].lower
    assert verify_intervals(polynomial, intervals) is None


@pytest.mark.parametrize("intervals", [
    (RootInterval(fmpq(1), fmpq(2)),),  # Incomplete coverage.
    (RootInterval(fmpq(1), fmpq(2)), RootInterval(fmpq(1), fmpq(2))),  # Same root twice.
    (RootInterval(fmpq(-3), fmpq(-2)), RootInterval(fmpq(1), fmpq(2))),  # No negative root inside.
    (RootInterval(fmpq(-1), fmpq(-2)), RootInterval(fmpq(1), fmpq(2))),  # Reversed interval.
])
def test_invalid_root_evidence_is_rejected(intervals):
    with pytest.raises(CertificationError):
        verify_intervals(fmpq_poly([-2, 0, 1]), intervals)


def test_repeated_roots_cannot_pass_sign_change_certificate():
    with pytest.raises(CertificationError):
        verify_intervals(fmpq_poly([0, 0, 1]),
                         (RootInterval(fmpq(-1), fmpq(0)), RootInterval(fmpq(0), fmpq(1))))


def test_interval_coordinate_evaluation_contains_the_true_points():
    representation = Representation(fmpq_poly([-2, 0, 1]),
                                    (fmpq_poly([0, 1]), fmpq_poly([0, 0, 1]), fmpq_poly([1])))
    with ctx.workprec(256):
        intervals = propose_intervals(representation.polynomial, 64)
        points = enclose_points(representation, intervals)
        assert all(point[2].contains(2) and point[3] == 1 for point in points)
        assert points[0][1].contains(-arb(2).sqrt())
        assert points[1][1].contains(arb(2).sqrt())


def interpolation_points():
    # The ten degree<=2 simplex-lattice nodes are unisolvent for quadratics.
    return tuple(tuple(arb(x) for x in (1, *node)) for node in monomials(2))


def test_unisolvent_points_have_a_strict_determinant_bound():
    with ctx.workprec(128):
        report = certify_determinants(interpolation_points())
    assert report.complete and report.checked == report.total == 1
    assert report.lower_bound > 0


def test_points_on_a_quadric_are_rejected():
    # Every row obeys x0*x1-x2*x3=0, exactly.
    points = tuple(tuple(arb(x) for x in (1, a*b, a, b)) for a in range(1, 3) for b in range(1, 6))
    with pytest.raises(CertificationError):
        certify_determinants(points)


def test_duplicate_point_is_rejected():
    points = interpolation_points()
    with pytest.raises(CertificationError):
        certify_determinants((*points[:-1], points[0]))


def test_wide_balls_are_inconclusive_instead_of_using_the_midpoint():
    points = interpolation_points()
    uncertain = tuple(arb(x.mid(), 100) for x in points[0])
    with pytest.raises(CertificationError):
        certify_determinants((uncertain, *points[1:]))


def test_prefix_is_never_reported_as_complete():
    points = (*interpolation_points(), tuple(arb(x) for x in (1, 3, 4, 5)))
    report = certify_determinants(points, limit=1)
    assert report.checked == 1 and report.total == 11 and not report.complete


def test_too_few_points_is_not_an_empty_success():
    with pytest.raises(CertificationError):
        certify_determinants(interpolation_points()[:9])
