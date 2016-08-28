from syn.types.a import Type, Numeric, Int, hashable

#-------------------------------------------------------------------------------
# Numeric

def test_numeric():
    x = 1
    t = Type.dispatch(x)
    assert isinstance(t, Numeric)
    assert type(t) is Int

    assert hashable(x) == x

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
