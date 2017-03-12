from syn.util.constraint import FunctionConstraint, AllDifferent

#-------------------------------------------------------------------------------
# FunctionConstraint

def test_functionconstraint():
    c = FunctionConstraint(lambda a, b: a == b, ('a', 'b'))
    assert c.check(b=1, a=1)
    assert not c.check(a=2, b=1)
    assert c.check(b=1, a=1, c=1)
    
#-------------------------------------------------------------------------------
# AllDifferent

def test_alldifferent():
    c = AllDifferent(('a', 'b', 'c'))
    assert c.check(a=1, b=2, c=3)
    assert not c.check(a=1, b=2, c=1)
    assert c.check(a=1, b=2, c=3, d=1)
    assert not c.check(a=1, b=2, c=1, d=1)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
