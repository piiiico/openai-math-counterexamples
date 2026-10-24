"""Exact identities, geometric boundaries, and deliberate corruption controls."""
from pathlib import Path
import subprocess
import sys

import pytest
import sympy as sp

from check import T, base_square, base_triangle, certificate, configuration, require_zero
import check


@pytest.mark.parametrize("base,count,coefficient", [
    (base_square, 12, 4), (base_triangle, 9, 3),
])
def test_complete_symbolic_certificate(base, count, coefficient):
    report = certificate(base())
    assert report["points"] == count
    assert report["spatial_coefficient"] == coefficient
    assert report["jet_coefficients_checked"] == 36


def test_field_normalization_and_failure():
    require_zero((T**2 - 1)/(T - 1) - T - 1)
    require_zero(sp.sqrt(3)**2 - 3)
    with pytest.raises(ValueError):
        require_zero(T - sp.Rational(1, 9))


@pytest.mark.parametrize("fault", ["central_weight", "same_rotation", "plain_derivative"])
def test_mutations_rejected(fault):
    with pytest.raises(ValueError):
        certificate(base_triangle(), fault=fault)


def test_nonisotropic_base_rejected():
    with pytest.raises(ValueError):
        certificate([(sp.Integer(1), sp.Integer(0)), (-sp.Integer(1), sp.Integer(0))])


@pytest.mark.parametrize("base", [
    [(sp.Integer(0), sp.Integer(0))],
    [(sp.Integer(1), sp.Integer(0))],
    [(2*x, 2*y) for x, y in base_square()],
])
def test_other_invalid_bases_rejected(base):
    with pytest.raises(ValueError):
        certificate(base)


def test_positive_cli(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["check.py"])
    assert check.main() == 0
    assert "all 72 jet coefficients verified" in capsys.readouterr().out


def test_geometric_degeneracy_is_separate_from_moments():
    # A formal rational-function identity is not distinctness at every t.
    points, _, _ = configuration(base_triangle())
    at_zero = {tuple(sp.simplify(x.subs(T, 0)) for x in p[1:]) for p in points}
    assert len(at_zero) == 3
    at_small = {tuple(sp.simplify(x.subs(T, sp.Rational(1, 9))) for x in p[1:]) for p in points}
    assert len(at_small) == 9


@pytest.mark.parametrize("optimized", [False, True])
def test_cli_control_exits_nonzero(optimized):
    args = [sys.executable] + (["-O"] if optimized else [])
    result = subprocess.run(args + [str(Path(__file__).with_name("check.py")),
                            "--negative-control", "central_weight"],
                            capture_output=True, text=True)
    assert result.returncode == 1
    assert "RESULT: rejected" in result.stdout


def test_control_cli_does_not_manufacture_rejection(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["check.py", "--negative-control", "central_weight"])
    monkeypatch.setattr(check, "certificate", lambda *args, **kwargs: {"test": "accepted"})
    assert check.main() == 0
