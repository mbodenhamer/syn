import collections
from nose.tools import assert_raises
from syn.sets import SetWrapper
from syn.util.constraint import Domain, Constraint, Problem

#-------------------------------------------------------------------------------
# Domain

def test_domain():
    d = Domain()
    d['a'] = 1
    assert d['a'] == 1
    assert list(d) == ['a']
    del d['a']
    assert list(d) == []

    d = Domain(a = [1,2], b = [3,4])
    assert d['a'] == SetWrapper([1, 2])
    assert d['b'] == SetWrapper([3, 4])
    assert d['a'].to_set() == {1, 2}

    assert isinstance(d, collections.Mapping)

#-------------------------------------------------------------------------------
# Constraint

def test_constraint():
    c = Constraint()
    assert_raises(NotImplementedError, c.check)

#-------------------------------------------------------------------------------
# Problem

def test_problem():
    c1 = Constraint(['a'])
    c2 = Constraint(['a', 'b'])
    p = Problem(Domain(a=[1, 2], b=[2, 3]), [c1, c2])
    
    assert p.var_constraint == dict(a = {c1, c2},
                                    b = {c2})

    assert_raises(ValueError, Problem, Domain(a=[1]), [c1, c2])

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
