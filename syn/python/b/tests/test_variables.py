from syn.base_utils import pyversion
from syn.python.b import Starred, Name
from .test_literals import examine
from .test_statements import examine as examine_

VER = pyversion()

#-------------------------------------------------------------------------------
# Name

def test_name():
    examine('foo')

    n = Name('x')
    assert n.emit() == 'x'
    assert n.emit(indent_level=1) == '    x'
    assert n.variables() == {'x'}

#-------------------------------------------------------------------------------
# Starred

def test_starred():
    if VER >= Starred.minver:
        examine_('*b = c')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
