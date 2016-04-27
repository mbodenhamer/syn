from syn.base import Base, Attr
from syn.conf import VarsMixin
from syn.five import STR

#-------------------------------------------------------------------------------
# VarsMixin

def test_varsmixin():
    class A(Base, VarsMixin):
        _opts = dict(init_validate = True)
        _attrs = dict(a = Attr(int),
                      b = Attr(float),
                      c = Attr(STR))

    a = A(a = 1, b = 1.2, c = 'abc')
    assert a.to_dict('vars', 'internal') == dict(a = 1, b = 1.2, c = 'abc')
    assert a._groups['internal'] == set(['_env'])
    assert a._groups['vars'] == set(['vars'])
    assert a._env == a.to_dict('vars', 'internal')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
