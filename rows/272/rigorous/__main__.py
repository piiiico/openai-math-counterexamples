"""Generate untrusted proposals, or verify a saved exhaustive certificate."""

import argparse
import hashlib
import json
from math import comb
from pathlib import Path
import platform
import sys
from time import perf_counter

import flint
import sympy

from .algebra import (CertificationError, generate_representation, load_pencil,
                      maximal_minors, verify_representation)
from .certificate import Certificate, decode_certificate, encode_certificate, encode_rational
from .enclosures import certify_determinants, enclose_points, propose_intervals

DIRECTORY = Path(__file__).resolve().parent


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate(path: Path, root_bits: int) -> dict:
    pencil = DIRECTORY / "pencil.json"
    minors = maximal_minors(load_pencil(pencil))
    representation = generate_representation(minors)
    verify_representation(minors, representation)
    intervals = propose_intervals(representation.polynomial, root_bits)
    certificate = Certificate(file_digest(pencil), representation, intervals)
    path.write_text(json.dumps(encode_certificate(certificate), indent=2) + "\n")
    return {"status": "candidate_generated", "certificate_sha256": file_digest(path),
            "real_roots_certified": len(intervals), "determinants_checked": 0}


def verify(path: Path, precision: int) -> dict:
    if precision < 32:
        raise CertificationError("ball arithmetic precision must be at least 32 bits")
    started = perf_counter()
    pencil = DIRECTORY / "pencil.json"
    certificate = decode_certificate(json.loads(path.read_text()))
    if certificate.pencil_sha256 != file_digest(pencil):
        raise CertificationError("certificate pencil digest does not match the input file")
    # Generation is deliberately absent from this path. Saved coefficients,
    # endpoints, and root counts must discharge the exact obligations again.
    minors = maximal_minors(load_pencil(pencil))
    verify_representation(minors, certificate.representation)
    with flint.ctx.workprec(precision):
        points = enclose_points(certificate.representation, certificate.intervals)
        if len(points) != 20:
            raise CertificationError("family 272 requires exactly twenty certified points")
        report = certify_determinants(points)
    if not report.complete or report.checked != comb(20, 10):
        raise CertificationError("family 272 requires all 184756 ten-point subsets")
    return {
        "status": "certified",
        "scope": "family272_projective_rank_loss_locus_and_quadratic_evaluation",
        "pencil_sha256": certificate.pencil_sha256,
        "certificate_sha256": file_digest(path),
        "exact_minor_identities": len(minors),
        "distinct_real_projective_points": len(points),
        "checked_subsets": report.checked,
        "total_subsets": report.total,
        "complete": report.complete,
        "ball_precision_bits": precision,
        "minimum_normalized_determinant_lower_bound": encode_rational(report.lower_bound),
        "subset_with_smallest_certified_lower_bound_zero_based": list(report.worst_subset),
        "elapsed_seconds": round(perf_counter() - started, 3),
        "software": {"python": platform.python_version(), "python_flint": flint.__version__,
                     "flint": flint.__FLINT_VERSION__, "sympy": sympy.__version__},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    generator = actions.add_parser("generate", help="write exact algebra/root proposals; does not certify determinants")
    generator.add_argument("--certificate", type=Path, default=DIRECTORY / "certificate.json")
    generator.add_argument("--root-bits", type=int, default=512)
    verifier = actions.add_parser("verify", help="verify saved algebra, roots, and every determinant")
    verifier.add_argument("--certificate", type=Path, default=DIRECTORY / "certificate.json")
    verifier.add_argument("--precision", type=int, default=1024)
    arguments = parser.parse_args(argv)
    try:
        result = (generate(arguments.certificate, arguments.root_bits) if arguments.action == "generate"
                  else verify(arguments.certificate, arguments.precision))
    except (CertificationError, OSError, ValueError) as error:
        print(json.dumps({"status": "not_certified", "reason": str(error)}))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
