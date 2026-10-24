from copy import deepcopy
from fractions import Fraction
import pytest
import check


def test_twenty_is_first_violation_and_unique_optimum():
    certificate = check.generate(40)
    check.verify(certificate)
    rows = {r['dimension']:r for r in certificate['states']}
    assert all(rows[d]['scaled_maximum'] == (d+1)*d**d for d in range(2,20))
    assert rows[20]['best_partitions'] == [[10,10]]
    assert Fraction(rows[20]['scaled_maximum'],21*20**20) == Fraction(22355476,22020096)


def test_first_three_factor_optimum():
    rows = check.generate(40)['states']
    first = next(r for r in rows if any(len(p)==3 for p in r['best_partitions']))
    assert first['dimension']==33
    assert first['best_partitions']==[[11,11,11]]


def test_simplex_and_partition_values():
    assert check.scaled_value((2,2)) == 864
    assert check.scaled_value((2,)) == 12
    assert check.scaled_value((10,10)) > check.scaled_value((20,))
    assert check.scaled_value((9,10)) < check.scaled_value((19,))


@pytest.mark.parametrize('fault',['maximum','partition','domain','optimal_set'])
def test_corrupted_certificates_reject(fault):
    certificate=check.generate(40)
    check.corrupt(certificate,fault)
    with pytest.raises(ValueError):check.verify(certificate)


def test_does_not_accept_unrequested_domain():
    with pytest.raises(ValueError,match='domain'):check.verify(check.generate(20))


def test_smaller_domain_is_explicit():
    check.verify(check.generate(6),expected_max=6)


@pytest.mark.parametrize('parts',[(1,2),(),(0,3),(2,-1),(2.0,3)])
def test_invalid_geometric_partitions(parts):
    with pytest.raises(ValueError):check.scaled_value(parts)


def test_invalid_certificate_schema_and_state_sequence():
    c=check.generate(4);c['schema_version']=2
    with pytest.raises(ValueError):check.verify(c,expected_max=4)
    c=check.generate(4);c['states'].insert(1,deepcopy(c['states'][0]))
    with pytest.raises(ValueError):check.verify(c,expected_max=4)


def test_incomplete_tie_witnesses_rejected():
    c=check.generate(40);c['states'][-1]['best_partitions']=[]
    with pytest.raises(ValueError):check.verify(c)
