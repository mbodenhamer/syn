import syn.util.constraint as con
import syn.util.constraint.b as bcon

#-------------------------------------------------------------------------------
# Constraint imports

def test_constaint_imports():
    assert con.Domain is bcon.Domain

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
