"""Exact serialization and end-to-end rejection of corrupted certificates."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

from flint import fmpq, fmpq_poly
import pytest

from .algebra import CertificationError, Representation
from .certificate import Certificate, decode_certificate, encode_certificate
from .enclosures import RootInterval
from .enclosures import DeterminantReport
from . import __main__ as cli


@pytest.fixture
def certificate():
    return Certificate("a" * 64, Representation(fmpq_poly([-2, 0, 1]),
                       (fmpq_poly([0, 1]), fmpq_poly([1, 2]), fmpq_poly([]))),
                       (RootInterval(fmpq(-3, 2), fmpq(-1)),
                        RootInterval(fmpq(1), fmpq(3, 2))))


def test_roundtrip_preserves_every_exact_number(certificate):
    encoded = encode_certificate(certificate)
    assert decode_certificate(json.loads(json.dumps(encoded))) == certificate
    assert encoded["representation"]["polynomial"] == [[-2, 1], [0, 1], [1, 1]]


@pytest.mark.parametrize("bad", [[1, 0], [1, -2], [True, 1], [0.5, 1], ["1", 2], [2, 4], [1]])
def test_malformed_or_noncanonical_rational_is_rejected(certificate, bad):
    data = encode_certificate(certificate)
    data["representation"]["polynomial"][0] = bad
    with pytest.raises(CertificationError):
        decode_certificate(data)


@pytest.mark.parametrize("alter", [
    lambda d: d.update(schema_version=True),
    lambda d: d.update(schema_version=2),
    lambda d: d.update(pencil_sha256="not a digest"),
    lambda d: d.update(unexpected=True),
    lambda d: d["representation"]["coordinates"].pop(),
    lambda d: d["root_intervals"][0].pop(),
    lambda d: d["representation"]["polynomial"].append([0, 1]),
])
def test_malformed_structure_is_rejected(certificate, alter):
    data = deepcopy(encode_certificate(certificate))
    alter(data)
    with pytest.raises(CertificationError):
        decode_certificate(data)


def test_cli_rejects_altered_exact_identity(tmp_path):
    data = json.loads(Path(__file__).with_name("certificate.json").read_text())
    coefficient = data["representation"]["polynomial"][0]
    coefficient[0] += coefficient[1]
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text(json.dumps(data))
    result = subprocess.run([sys.executable, "-m", __package__, "verify", "--certificate", str(corrupt)],
                            text=True, capture_output=True)
    assert result.returncode == 1
    assert json.loads(result.stdout)["status"] == "not_certified"
    assert "not zero" in json.loads(result.stdout)["reason"]


def test_cli_rejects_incorrect_source_digest(tmp_path):
    data = json.loads(Path(__file__).with_name("certificate.json").read_text())
    data["pencil_sha256"] = "0" * 64
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text(json.dumps(data))
    result = subprocess.run([sys.executable, "-m", __package__, "verify", "--certificate", str(corrupt)],
                            text=True, capture_output=True)
    assert result.returncode == 1
    assert "digest" in json.loads(result.stdout)["reason"]


@pytest.mark.parametrize("report", [
    DeterminantReport(1, 184756, fmpq(1), ()),
    DeterminantReport(92378, 92378, fmpq(1), ()),
])
def test_full_verifier_cannot_promote_an_incomplete_or_wrong_domain_report(monkeypatch, report):
    monkeypatch.setattr(cli, "certify_determinants", lambda points: report)
    with pytest.raises(CertificationError, match="all 184756"):
        cli.verify(Path(__file__).with_name("certificate.json"), 1024)
