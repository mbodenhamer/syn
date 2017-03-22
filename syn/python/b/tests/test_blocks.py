from .test_statements import examine
from syn.python.b import Block

#-------------------------------------------------------------------------------
# Block

def test_block():
    Block

#-------------------------------------------------------------------------------
# If

def test_if():
    examine('if 1:\n    a = 1')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
