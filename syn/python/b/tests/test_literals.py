from functools import partial
from syn.python.b import Literal, from_source
from syn.base_utils import compose

eparse = compose(partial(from_source, mode='eval'), str)

#-------------------------------------------------------------------------------
# Base Class

def test_literal():
    Literal()

#-------------------------------------------------------------------------------
# Num

def test_num():
    tree = eparse(1)
    tree.emit() == '1'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
