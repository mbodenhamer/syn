from syn.types.a.ne import Value, FindNE

#-------------------------------------------------------------------------------
# Value

def test_value():
    v = Value(1)
    assert v() == 1
    assert v != 1

    assert v == Value(1)
    assert v != Value(2)

#-------------------------------------------------------------------------------
# FindNe

def test_findNe():
    FindNE

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
