import os
from syn.base import Attr
from syn.conf import Vars
from syn.five import STR

#-------------------------------------------------------------------------------
# Vars

def test_vars():
    class A(Vars):
        _opts = dict(init_validate = True)
        _attrs = dict(a = Attr(int),
                      b = Attr(float),
                      c = Attr(STR),
                      d = Attr(STR, optional=True))

    a1 = ['a=1', 'b=2.3', 'c=abc', 'd']
    assert A.coerce(a1) == A(a = 1, b = 2.3, c = 'abc', d = '')

    a2 = ['a=1', 'b={{ a + 2 }}', 'c=ab{{ b + 2 }}']
    assert A.coerce(a2) == A(a = 1, b = 3.0, c = 'ab5.0')

    class B(Vars):
        _opts = dict(init_validate = True)
        _attrs = dict(foo = Attr(STR))

    os.environ['FOO'] = 'bar'
    assert B.coerce(['foo={{ FOO }}']) == B(foo = '')
    
    B._opts.env_default = True
    assert B.coerce(['foo={{ FOO }}']) == B(foo = 'bar')

#-------------------------------------------------------------------------------
# VarsMixin

def test_varsmixin():
    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
