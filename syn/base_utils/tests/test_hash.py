from syn.base_utils import is_hashable

#-------------------------------------------------------------------------------
# is_hashable

def test_is_hashable():
    assert is_hashable(3)
    assert not is_hashable(dict(a = 3))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
