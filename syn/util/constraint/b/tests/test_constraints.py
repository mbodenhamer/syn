from operator import eq
from syn.util.constraint import FunctionConstraint, AllDifferentConstraint, \
    EqualConstraint, Domain

#-------------------------------------------------------------------------------
# FunctionConstraint

def test_functionconstraint():
    c = FunctionConstraint(eq, ('a', 'b'))
    assert c.check(b=1, a=1)
    assert not c.check(a=2, b=1)
    assert c.check(b=1, a=1, c=1)
    assert c.display() == "Function({}, a, b)".format(eq)

#-------------------------------------------------------------------------------
# AllDifferent

def test_alldifferentconstraint():
    c = AllDifferentConstraint(('a', 'b', 'c'))
    assert c.check(a=1, b=2, c=3)
    assert not c.check(a=1, b=2, c=1)
    assert c.check(a=1, b=2, c=3, d=1)
    assert not c.check(a=1, b=2, c=1, d=1)
    assert c.display() == "AllDifferent(a, b, c)"

#-------------------------------------------------------------------------------
# EqualConstraint

def test_equalconstraint():
    c = EqualConstraint('a', 2)
    assert c.check(a=2)
    assert not c.check(a=1)
    assert c.check(a=2, b=1)
    assert not c.check(a=1, b=1)
    assert c.display() == 'a == 2'

    d = Domain(a = [1, 2, 3])
    assert d['a'].to_set() == {1, 2, 3}

    c.preprocess(d)
    assert d['a'].to_set() == {2,}

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
