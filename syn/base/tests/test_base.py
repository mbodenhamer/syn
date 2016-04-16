import syn.base
import syn.base.a

#-------------------------------------------------------------------------------
# Base

def test_base_import():
    assert syn.base.Base is syn.base.a.Base

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
