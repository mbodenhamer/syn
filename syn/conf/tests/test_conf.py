from nose.tools import assert_raises
from syn.conf import YAMLMixin
from syn.conf.conf import ConfMixin
from syn.base import Base, Attr
from syn.five import STR
from syn.type import List

#-------------------------------------------------------------------------------
# ConfMixin

def test_confmixin():
    assert_raises(NotImplementedError, ConfMixin.from_file, None)

#-------------------------------------------------------------------------------
# YAML


class A(Base, YAMLMixin):
    _opts = dict(init_validate = True)
    _attrs = dict(a = Attr(int),
                  b = Attr(float),
                  c = Attr(STR))

YAML_A = '''a: 1
b: 2.3
c: abc'''

class B(Base, YAMLMixin):
    _opts = dict(init_validate = True)
    _attrs = dict(a = Attr(int),
                  b = Attr(List(A)))
    
YAML_B = '''a: 2
b: 
   - a: 1
     b: 2.3
     c: abc

   - a: 2
     b: 3.4
     c: def
'''

def test_yamlmixin():
    assert A.from_string(YAML_A) == A(a=1, b=2.3, c='abc')
    assert B.from_string(YAML_B) == B(a=2, b=[A(a=1, b=2.3, c='abc'),
                                              A(a=2, b=3.4, c='def')])

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
