import syn.base
import syn.base.b

#-------------------------------------------------------------------------------
# Base imports

def test_base_imports():
    assert syn.base.Base is syn.base.b.Base
    assert syn.base.Attr is syn.base.b.Attr
    assert syn.base.Attrs is syn.base.b.Attrs

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
