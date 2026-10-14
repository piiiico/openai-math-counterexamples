"""Versioned JSON certificates contain exact rationals, never decimal estimates."""

from dataclasses import dataclass
from math import gcd

from flint import fmpq, fmpq_poly

from .algebra import CertificationError, Representation
from .enclosures import RootInterval


@dataclass(frozen=True)
class Certificate:
    pencil_sha256: str
    representation: Representation
    intervals: tuple[RootInterval, ...]


def encode_rational(value: fmpq) -> list[int]:
    return [int(value.numerator), int(value.denominator)]


def decode_rational(value: object) -> fmpq:
    if (not isinstance(value, list) or len(value) != 2
            or any(type(x) is not int for x in value)
            or value[1] <= 0 or gcd(*value) != 1):
        raise CertificationError("expected a reduced rational [integer numerator, positive denominator]")
    return fmpq(*value)


def decode_polynomial(value: object) -> fmpq_poly:
    if not isinstance(value, list):
        raise CertificationError("polynomial coefficients must be a list in ascending degree")
    coefficients = [decode_rational(x) for x in value]
    if coefficients and coefficients[-1] == 0:
        raise CertificationError("polynomial coefficient lists must not have trailing zeros")
    return fmpq_poly(coefficients)


def require_fields(value: object, fields: set[str]) -> None:
    if not isinstance(value, dict) or set(value) != fields:
        raise CertificationError(f"expected exactly these fields: {sorted(fields)}")


def encode_certificate(certificate: Certificate) -> dict:
    representation = certificate.representation
    return {
        "schema_version": 1,
        "pencil_sha256": certificate.pencil_sha256,
        "representation": {
            "polynomial": [encode_rational(x) for x in representation.polynomial.coeffs()],
            "coordinates": [[encode_rational(x) for x in p.coeffs()] for p in representation.coordinates],
        },
        "root_intervals": [[encode_rational(i.lower), encode_rational(i.upper)] for i in certificate.intervals],
    }


def decode_certificate(data: object) -> Certificate:
    require_fields(data, {"schema_version", "pencil_sha256", "representation", "root_intervals"})
    if type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise CertificationError("unsupported certificate schema version")
    digest = data["pencil_sha256"]
    try:
        if not isinstance(digest, str) or len(digest) != 64 or bytes.fromhex(digest).hex() != digest:
            raise ValueError()
    except ValueError as error:
        raise CertificationError("expected a canonical SHA-256 pencil digest") from error
    representation = data["representation"]
    require_fields(representation, {"polynomial", "coordinates"})
    coordinates = representation["coordinates"]
    if not isinstance(coordinates, list) or len(coordinates) != 3:
        raise CertificationError("expected three affine coordinate polynomials")
    intervals = data["root_intervals"]
    if not isinstance(intervals, list) or any(not isinstance(i, list) or len(i) != 2 for i in intervals):
        raise CertificationError("expected a list of pairs of rational endpoints")
    return Certificate(digest,
                       Representation(decode_polynomial(representation["polynomial"]),
                                      tuple(decode_polynomial(p) for p in coordinates)),
                       tuple(RootInterval(decode_rational(a), decode_rational(b)) for a, b in intervals))
