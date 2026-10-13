"""Tests distinguish exact identities from close numerical agreement."""

from dataclasses import replace
import json
from pathlib import Path

from flint import fmpq_poly
import pytest

from .algebra import (CertificationError, generate_representation, load_pencil,
                      maximal_minors, reduction_matrices, verify_representation)
from .independent_minor_check import check

DATA = Path(__file__).with_name("pencil.json")


@pytest.fixture(scope="module")
def minors():
    return maximal_minors(load_pencil(DATA))


@pytest.fixture(scope="module")
def representation(minors):
    return generate_representation(minors)


def test_pinned_quartic_matrix_has_the_published_nonzero_residue(minors):
    high, low = reduction_matrices(minors)
    assert high.nrows() == high.ncols() == 15
    assert low.nrows() == 15 and low.ncols() == 20
    assert int(high.det()) % 41 == 40


def test_all_fifteen_minor_identities_hold_exactly(minors, representation):
    assert len(minors) == 15
    assert representation.polynomial.degree() == 20
    assert representation.coordinates[0] == fmpq_poly([0, 1])
    assert verify_representation(minors, representation) is None


def test_permutation_expansion_independently_matches_all_minor_coefficients(minors):
    check(load_pencil(DATA), minors)


def test_permutation_expansion_detects_an_altered_minor_coefficient(minors):
    altered = [dict(minor) for minor in minors]
    constant = (0, 0, 0)
    altered[0][constant] = altered[0].get(constant, 0) + 1
    with pytest.raises(CertificationError):
        check(load_pencil(DATA), tuple(altered))


@pytest.mark.parametrize("coordinate", [0, 1, 2])
def test_altered_coordinate_is_rejected(minors, representation, coordinate):
    coordinates = list(representation.coordinates)
    coordinates[coordinate] += 1
    with pytest.raises(CertificationError):
        verify_representation(minors, replace(representation, coordinates=tuple(coordinates)))


def test_altered_polynomial_is_rejected(minors, representation):
    with pytest.raises(CertificationError):
        verify_representation(minors, replace(representation, polynomial=representation.polynomial + 1))


def test_wrong_degree_is_rejected(minors, representation):
    with pytest.raises(CertificationError):
        verify_representation(minors, replace(representation, polynomial=fmpq_poly([1, 1])))


def test_verifier_rejects_zero_minors_even_when_every_substitution_vanishes(representation):
    with pytest.raises(CertificationError, match="invertible H"):
        verify_representation(tuple({} for _ in range(15)), representation)


def test_singular_quartic_matrix_does_not_certify_completeness():
    matrices = load_pencil(DATA)
    flattened = tuple(tuple(row if i < 4 else (0, 0, 0, 0) for i, row in enumerate(matrix)) for matrix in matrices)
    with pytest.raises(CertificationError):
        generate_representation(maximal_minors(flattened))


@pytest.mark.parametrize("bad_entry", [0.1, True, "6"])
def test_inexact_or_noninteger_input_is_rejected(tmp_path, bad_entry):
    data = json.loads(DATA.read_text())
    data["matrices"][0][0][0] = bad_entry
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    with pytest.raises(CertificationError):
        load_pencil(path)


def test_wrong_matrix_shape_is_rejected(tmp_path):
    data = json.loads(DATA.read_text())
    data["matrices"].pop()
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(data))
    with pytest.raises(CertificationError):
        load_pencil(path)
