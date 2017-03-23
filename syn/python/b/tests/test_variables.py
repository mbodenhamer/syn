from syn.base_utils import pyversion
from syn.python.b import Starred
from .test_literals import examine
from .test_statements import examine as examine_

VER = pyversion()

#-------------------------------------------------------------------------------
# Name

def test_name():
    examine('foo')

#-------------------------------------------------------------------------------
# Starred

def test_starred():
    if VER >= Starred.minver:
        examine_('*b = c')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
