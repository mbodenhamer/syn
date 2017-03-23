from syn.python.b import from_source
from functools import partial
from syn.base_utils import compose
from .test_literals import examine

eparse = compose(partial(from_source, mode='eval'), str)

#-------------------------------------------------------------------------------
# Name

def test_name():
    examine('foo')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
