"""Mathematical failure controls for the exact channel certificate."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest
from flint import fmpz_mat

from .checker import (
    ChannelCertificateError, build, certify, decode, reshuffle, unreshuffle, verify_saved,
)

SOURCE = Path(__file__).resolve().parents[1] / "family272_tensor" / "certificate.json"
if not SOURCE.exists():
    SOURCE = Path(__file__).resolve().parents[1] / "tensor" / "certificate.json"


@pytest.fixture(scope="module")
def tensor():
    return json.loads(SOURCE.read_text())


@pytest.fixture(scope="module")
def built(tensor):
    return build(tensor)


def test_complete_exact_channel(built):
    result, certificate = certify(built)
    assert result["dimension"] == 21
    assert result["denominator"] == 4923191
    assert result["square_corner_trace_numerator"] == 1381419987480
    assert result["square_corner_rank"] == 80
    assert result["flag_product_vector_in_square_range"] is True
    assert result["secret_key_claim_checked"] is False
    assert certificate["square_choi"]["shape"] == [441, 441]


def test_missing_failure_branch_is_not_trace_preserving(built):
    broken = replace(built, channel=fmpz_mat(built.channel), square=fmpz_mat(built.square))
    broken.channel[20, 20] = 0
    with pytest.raises(ChannelCertificateError, match="trace preservation"):
        certify(broken)


def test_lost_absorbing_flag_is_detected(built):
    broken = replace(built, channel=fmpz_mat(built.channel), square=fmpz_mat(built.square))
    broken.channel[440, 440] = 0
    with pytest.raises(ChannelCertificateError, match="trace preservation"):
        certify(broken)


def test_wrong_composition_is_detected(built):
    broken = replace(built, channel=fmpz_mat(built.channel), square=fmpz_mat(built.square))
    broken.square[0, 0] += 1
    with pytest.raises(ChannelCertificateError, match="composition"):
        certify(broken)


def test_partial_transpose_failure_control(built):
    broken = replace(built, channel=fmpz_mat(built.channel), square=fmpz_mat(built.square))
    broken.channel[10, 32] += 1
    broken.channel[32, 10] += 1
    with pytest.raises(ChannelCertificateError, match="transpose"):
        certify(broken)


def test_saved_certificate_and_corruption(tensor, built):
    _, certificate = certify(built)
    assert verify_saved(tensor, certificate)["status"] == "certified"
    broken = deepcopy(certificate)
    broken["channel_choi"]["entries"][0][2] += 1
    with pytest.raises(ChannelCertificateError, match="saved certificate"):
        verify_saved(tensor, broken)


def test_wrong_dependency_is_detected(tensor):
    broken = deepcopy(tensor)
    broken["s_kraus"][0][0][0] += 1
    with pytest.raises(ChannelCertificateError, match="pencil"):
        build(broken)


def test_sparse_decode_rejects_duplicate_or_outside_entries():
    for entries in [[[0, 0, 1], [0, 0, 2]], [[2, 0, 1]], [[0, 0, 0]]]:
        with pytest.raises(ChannelCertificateError):
            decode(dict(shape=[2, 2], entries=entries))


def test_choi_superoperator_permutations_are_inverse_not_identical():
    matrix = fmpz_mat(4, 4, list(range(16)))
    assert unreshuffle(reshuffle(matrix, 2), 2) == matrix
    assert reshuffle(reshuffle(matrix, 2), 2) != matrix


def test_command_line_and_optimized_failure_control(tensor, built, tmp_path):
    _, certificate = certify(built)
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps(certificate))
    command = [sys.executable, "-O", "-m", __package__, str(SOURCE), "--certificate", str(path)]
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["channel_choi_rank"] == 51
    certificate["square_choi"]["entries"][0][2] += 1
    path.write_text(json.dumps(certificate))
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    assert completed.returncode == 1
    assert json.loads(completed.stdout)["status"] == "not_certified"
