"""Controls for tensor normalization, PPT premises, and kernel identities."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from flint import fmpz_mat

from .checker import TensorCertificateError, transpose_fixed, verify, verify_saved


@pytest.fixture
def pencil():
    return json.loads(Path(__file__).with_name("certificate.json").read_text())["pencil"]


def test_exact_tensor_certificate_and_normalization(pencil):
    # A missing factor from the unnormalised exterior embeddings changes this
    # hand-derived value: four times the source's 6 * 36**4.
    report = verify(pencil)
    assert report["status"] == "certified"
    assert report["nonzero_product_value"] == 40310784
    assert report["kernel_polynomial_identities"] == 100


def test_mutated_pencil_fails_ppt_premise(pencil):
    # This off-diagonal mutation breaks M_0^T M_1 symmetry.
    damaged = deepcopy(pencil)
    damaged[1][0][1] += 1
    with pytest.raises(TensorCertificateError, match="block symmetry"):
        verify(damaged)


def test_identity_complement_fails_kernel_identity(pencil):
    # The identity is still orthogonal and gives CP compositions, but it does
    # not send an exterior two-vector to its complementary pair.
    wrong = [[int(i == j) for j in range(6)] for i in range(6)]
    with pytest.raises(TensorCertificateError, match="kernel"):
        verify(pencil, complement=wrong)


def test_zero_pencil_does_not_certify_nonzero_composite():
    with pytest.raises(TensorCertificateError, match="nonzero"):
        verify([[[0] * 4 for _ in range(6)] for _ in range(4)])


def test_large_integer_scaling_has_no_fixed_width_overflow(pencil):
    scale = 10**6
    scaled = [[[scale * x for x in row] for row in matrix] for matrix in pencil]
    report = verify(scaled)
    # L is quadratic, S0 is quartic, and the composite is degree eight in M.
    assert report["nonzero_product_value"] == 40310784 * scale**8
    assert report["choi_rank"] == 80


def test_nonorthogonal_complement_is_rejected(pencil):
    with pytest.raises(TensorCertificateError, match="orthogonal"):
        verify(pencil, complement=[[2 * int(i == j) for j in range(6)] for i in range(6)])


@pytest.mark.parametrize("output", [False, True])
def test_entangled_choi_fails_partial_transpose_identity(output):
    # Choi matrix of the two-dimensional identity map: CP but not PPT.
    vector = fmpz_mat([[1], [0], [0], [1]])
    assert not transpose_fixed(vector * vector.transpose(), 2, 2, output=output)


def test_saved_certificate_replays_against_supplied_pencil(pencil):
    certificate = json.loads(Path(__file__).with_name("certificate.json").read_text())
    assert verify_saved(pencil, certificate)["status"] == "certified"


@pytest.mark.parametrize("field", ["choi", "s_kraus", "maximal_minor_coefficients", "kernel_multipliers"])
def test_changed_certificate_obligation_is_rejected(pencil, field):
    certificate = json.loads(Path(__file__).with_name("certificate.json").read_text())
    if field == "s_kraus":
        certificate[field][0][0][0] += 1
    elif field == "kernel_multipliers":
        certificate[field][0][0][0] += 1
    else:
        certificate[field][0][0] += 1
    with pytest.raises(TensorCertificateError, match="certificate"):
        verify_saved(pencil, certificate)


def test_wrong_source_pencil_is_rejected(pencil):
    certificate = json.loads(Path(__file__).with_name("certificate.json").read_text())
    pencil[0][0][0] += 1
    with pytest.raises(TensorCertificateError, match="pencil"):
        verify_saved(pencil, certificate)


@pytest.mark.parametrize("optimized", [False, True])
def test_cli_success_and_mutation_exit_codes(pencil, tmp_path, optimized):
    source = tmp_path / "pencil.json"
    source.write_text(json.dumps({"matrices": pencil}))
    command = [sys.executable] + (["-O"] if optimized else []) + ["-m", __package__, str(source)]
    package_root = Path(__file__).resolve().parents[len(__package__.split("."))]
    good = subprocess.run(command, cwd=package_root, capture_output=True, text=True, check=False)
    assert good.returncode == 0, good.stderr
    assert json.loads(good.stdout)["status"] == "certified"
    damaged = json.loads(Path(__file__).with_name("certificate.json").read_text())
    damaged["choi"][0][0] += 1
    bad_file = tmp_path / "bad.json"
    bad_file.write_text(json.dumps(damaged))
    bad = subprocess.run(command + ["--certificate", str(bad_file)], cwd=package_root,
                         capture_output=True, text=True, check=False)
    assert bad.returncode == 1
    assert json.loads(bad.stdout)["status"] == "not_certified"
