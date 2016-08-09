from syn.schema.b import Sequence

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    Sequence

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
