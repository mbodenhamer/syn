import syn.base
import syn.base.a

#-------------------------------------------------------------------------------
# Base imports

def test_base_imports():
    assert syn.base.Base is syn.base.a.Base
    assert syn.base.Attr is syn.base.a.Attr

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
