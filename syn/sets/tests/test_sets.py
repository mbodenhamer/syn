import syn.sets
import syn.sets.b

#-------------------------------------------------------------------------------
# Sets imports

def test_sets_imports():
    assert syn.sets.SetNode is syn.sets.b.SetNode

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
