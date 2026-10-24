from fractions import Fraction as F
import pytest
import check


def test_complete_budget_at_coarser_mesh():
    result = check.budget(F(1, 2000), F(1, 1000), F(1, 500000))
    assert result['coverage_gap'] == F(247, 2000000)
    assert result['area_saving'] == F(1662287, 3072000000000000)


def test_failed_budget_is_not_counterexample():
    with pytest.raises(ValueError, match='sufficient coverage'):
        check.budget(F(1, 2000), F(1, 1000), F(1, 1000))
    assert check.covered((F(0), F(0), F(1, 2)), [F(-1), F(1)], F(1, 2), F(0))


@pytest.mark.parametrize('tau,eta,gap', [(F(0),F(0),F(1)),(F(1),F(0),F(1)),(F(1,2),F(-1),F(1)),(F(1,2),F(1),F(1)),(F(1,2),F(0),F(0)),(F(1,2),F(0),F(3))])
def test_invalid_budget_inputs(tau, eta, gap):
    with pytest.raises(ValueError):
        check.budget(tau,eta,gap)


def test_exact_identity_obligations():
    assert check.identities() >= 8


@pytest.mark.parametrize('fault',['radial_sign','secant_sign','integral'])
def test_symbolic_mutations(fault):
    with pytest.raises(ValueError, match='identity'):
        check.identities(fault)


def test_unenlarged_cover_has_real_gap():
    point=(F(1,10), F(3,10), F(21,40));nodes=[F(-1),F(0),F(1)]
    assert not check.covered(point,nodes,F(1,2),F(0),enlarge=False)
    assert check.covered(point,nodes,F(1,2),F(0))


def test_boundary_vertices_and_nonuniform_mesh():
    nodes=[F(-1),F(-1,3),F(1,4),F(1)]
    for point in [(F(1),F(0),F(0)),(F(-1),F(0),F(0)),(F(0),F(1),F(1)),(F(0),F(-1),F(1))]:
        assert check.covered(point,nodes,F(1,2),F(0))


def test_invalid_partition_and_point():
    with pytest.raises(ValueError):check.covered((F(0),F(0),F(0)),[F(-1),F(-1),F(1)],F(1,2),F(0))
    with pytest.raises(ValueError):check.covered((F(2),F(0),F(0)),[F(-1),F(1)],F(1,2),F(0))


def test_first_crossing_does_not_require_monotonicity():
    assert check.first_crossing([F(0),F(3),F(-2),F(1)],F(1,2))==0
    assert check.first_crossing([F(0),F(3),F(-2),F(1)],F(0))==0
    with pytest.raises(ValueError):check.first_crossing([F(1),F(0)],F(1,2))


def test_zero_margin_and_nonpositive_area_certificate():
    with pytest.raises(ValueError,match='sufficient coverage'):check.budget(F(1,10),F(0),F(1,1000))
    with pytest.raises(ValueError,match='strict area'):check.budget(F(1,100),F(1,8),F(1,10000))


def test_zero_coverage_gap_is_allowed():
    tau=F(1,2000);gap=F(1,500000)
    eta=(F(7,4)*tau+gap/(4*tau)+gap/4)/(2*(1-tau))
    result=check.budget(tau,eta,gap)
    assert result['coverage_gap']==0
    assert result['area_saving']>0


def test_minimum_uniform_n_for_this_budget_only():
    with pytest.raises(ValueError,match='sufficient coverage'):
        check.budget(F(1,2000),F(1,1000),F(2,890124))
    assert check.budget(F(1,2000),F(1,1000),F(2,890125))['coverage_gap']==F(1,1780250000)
