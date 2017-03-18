import syn.tagmathon as st
import syn.tagmathon.b as bst

#-------------------------------------------------------------------------------
# Test Imports

def test_imports():
    assert st.SyntagmathonNode is bst.SyntagmathonNode

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
