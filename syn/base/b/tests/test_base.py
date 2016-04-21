import six
from nose.tools import assert_raises
from syn.base.b import Base, Attr
from syn.base_utils import assert_equivalent, assert_pickle_idempotent, \
    assert_deepcopy_idempotent, assert_inequivalent, assert_type_equivalent, \
    get_mod

if six.PY2:
    str = unicode

#-------------------------------------------------------------------------------
# Test basic functionality

class A(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(float),
                  c = Attr(str, optional=True))
    _opts = dict(init_validate = True)

class A2(A):
    _opts = dict(id_equality = True)
    _attrs = dict(b = Attr(float, group=A.groups_enum().getstate_exclude))

def test_base():
    kwargs = dict(a=5, b=3.4, c=u'abc')
    obj = A(**kwargs)

    assert obj.a == 5
    assert obj.b == 3.4
    assert obj.c == u'abc'
    
    assert obj.to_dict() == kwargs

    assert obj != 5
    assert_equivalent(obj, A(**kwargs))
    assert_inequivalent(obj, A(a=6, b=3.4, c=u'abc'))

    assert A(a=5, b=3.4).to_dict() == dict(a=5, b=3.4)

    assert_deepcopy_idempotent(obj)
    assert_pickle_idempotent(obj)

    assert_raises(TypeError, A, a=5.1, b=3.4)
    assert_raises(AttributeError, A, a=5)

    assert_equivalent(A(**kwargs), A(**kwargs))
    assert_inequivalent(A2(**kwargs), A2(**kwargs))
    assert_raises(AssertionError, assert_pickle_idempotent, A2(**kwargs))

    obj2 = A2(**kwargs)
    assert_type_equivalent(obj2.to_dict(), dict(a=5, b=3.4, c=u'abc'))
    assert obj2.to_dict('getstate_exclude', include=True) == dict(b=3.4)

#-------------------------------------------------------------------------------
# Test Positional Args

class B(A):
    _attrs = dict(b = Attr(float, default=1.2))
    _opts = dict(args = ('a', 'b'))

def test_positional_args():
    obj = B(5, 3.4, c=u'abc')

    assert obj.a == 5
    assert obj.b == 3.4
    assert obj.c == u'abc'

    assert B(5).to_dict() == dict(a=5, b=1.2)

    assert_raises(TypeError, B, 1, 2, 3)
    assert_raises(TypeError, B, 1, 2, a=1)

#-------------------------------------------------------------------------------
# Test arg coercion

class C(B):
    _opts = dict(coerce_args = True)

def test_arg_coercion():
    obj = C(5.1, 3)
    
    assert obj.a == 5
    assert obj.b == 3.0

    assert isinstance(obj.a, int)
    assert isinstance(obj.b, float)

#-------------------------------------------------------------------------------
# Test optional None

class D(C):
    _opts = dict(optional_none = True)

def test_optional_none():
    obj = D(5, 3.4)

    assert obj.a == 5
    assert obj.b == 3.4
    assert obj.c is None
    obj.validate()

#-------------------------------------------------------------------------------
# Test call


class E(B):
    _attrs = dict(d = Attr(list, None, call=list))

def test_call():
    obj = E(1, 2.1)
    
    assert obj.to_dict() == dict(a = 1,
                                 b = 2.1,
                                 d = [])

    assert E(1, 2.1, d=(1, 2)).to_dict() == dict(a = 1,
                                                 b = 2.1,
                                                 d = [1, 2])
    

#-------------------------------------------------------------------------------
# Test init

class F(B):
    _opts = dict(init_order = ('d', 'e'))
    _attrs = dict(d = Attr(float, internal=True, 
                           init=lambda self: self.a + self.b),
                  e = Attr(float, internal=True,
                           init=lambda self: self.d + self.a))

class G(F):
    _attrs = dict(f = Attr(float, internal=True,
                           init=lambda self: 2.0 * self.a))

def test_init():
    obj = F(5, 3.4)
    assert obj.d == 8.4
    assert obj.e == 13.4

    obj = G(5, 3.4)
    assert obj.d == 8.4
    assert obj.e == 13.4
    assert obj.f == 10.0

#-------------------------------------------------------------------------------
# Test repr

class H(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(int, group='repr_exclude'))

def test_repr():
    obj = H(a = 1, b = 2)
    assert repr(obj) == "<{}.H {{'a': 1}}>".format(get_mod(H))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
