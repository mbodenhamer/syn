import syn.type
import syn.type.a

#-------------------------------------------------------------------------------
# Type imports

def test_type_imports():
    assert syn.type.Type is syn.type.a.Type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
