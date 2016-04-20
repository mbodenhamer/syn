import six
from nose.tools import assert_raises
from syn.type.a import (Type, ValuesType, MultiType, TypeType, AnyType,
                        TypeExtension)

#-------------------------------------------------------------------------------
# Type

def test_type():
    t = Type()

    assert_raises(NotImplementedError, t.check, 1)
    assert_raises(NotImplementedError, t.coerce, 1)
    assert_raises(NotImplementedError, t.validate, 1)

#-------------------------------------------------------------------------------
# AnyType

def test_anytype():
    t = AnyType()

    t.check(1)
    assert t.coerce(1) == 1
    t.validate(1)

#-------------------------------------------------------------------------------
# TypeType

class Foo(object):
    def __init__(self, value):
        self.value = value

    def validate(self):
        assert self.value > 5

class Bar(Foo):
    @classmethod
    def coerce(cls, value):
        return Bar(value + 1)

def test_typetype():
    t = TypeType(int)
    assert t.type is int
    assert not t.call_coerce
    assert not t.call_validate

    t.check(1)
    assert_raises(TypeError, t.check, 1.2)
    assert t.query(1)
    assert not t.query(1.2)
    res, e = t.query_exception(1)
    assert res
    assert e is None
    res, e = t.query_exception(1.2)
    assert not res
    assert isinstance(e, TypeError)
    assert t.coerce(1.2) == 1
    assert_raises(TypeError, t.coerce, 'abc')
    t.validate(1)
    assert_raises(TypeError, t.validate, 1.2)


    f = TypeType(Foo)
    assert f.type is Foo
    assert not f.call_coerce
    assert f.call_validate

    f.check(Foo(2))
    assert_raises(TypeError, f.check, 2)
    f1 = f.coerce(1)
    assert isinstance(f1, Foo)
    assert f1.value == 1
    assert_raises(TypeError, f.validate, 6)
    assert_raises(AssertionError, f.validate, Foo(5))
    f.validate(Foo(6))


    b = TypeType(Bar)
    assert b.type is Bar
    assert b.call_coerce
    assert b.call_validate

    b.check(Bar(2))
    assert_raises(TypeError, b.check, Foo(2))
    b1 = b.coerce(1)
    assert isinstance(b1, Bar)
    assert b1.value == 2
    assert_raises(TypeError, b.validate, 6)
    assert_raises(AssertionError, b.validate, Bar(5))
    b.validate(Bar(6))

#-------------------------------------------------------------------------------
# ValuesType

def test_valuestype():
    t = ValuesType({1, 1.2, u'b'})
    
    t.check(1)
    t.check(1.2)
    t.check(u'b')
    assert_raises(TypeError, t.check, 2)

    assert t.coerce(1) == 1
    assert_raises(TypeError, t.coerce, 2)

    t.validate(1)
    assert_raises(TypeError, t.validate, 2)

#-------------------------------------------------------------------------------
# MultiType

def test_multitype():
    import math

    t = MultiType((int, float))
    assert t.is_typelist
    assert t.query(1)
    assert t.query(1.2)
    assert not t.query(u'a')

    assert t.coerce(1.2) == 1
    assert t.coerce(u'inf') == float(u'inf')
    assert_raises(TypeError, t.coerce, u'abc')

    t.validate(1)
    assert_raises(TypeError, t.validate, u'abc')


    t = MultiType((int, Foo, ValuesType([math.pi, math.e])))
    assert not t.is_typelist

    assert t.query(1)
    assert t.query(Foo(2))
    assert t.query(math.pi)
    assert not t.query(3.4)

    assert t.coerce(1) == 1
    f = t.coerce(u'abc')
    assert isinstance(f, Foo)
    assert f.value == u'abc'
    
    t.validate(1)
    t.validate(Foo(6))
    assert_raises(TypeError, t.validate, 3.4)
    assert_raises(AssertionError, t.validate, Foo(5))

    t = MultiType(six.string_types)
    t.validate('abc')
    t.validate('abc')
    t.validate(u'abc')
    assert_raises(TypeError, t.validate, 3.4)

#-------------------------------------------------------------------------------
# dispatch_type

def test_dispatch_type():
    t = Type.dispatch(None)
    assert isinstance(t, AnyType)

    t = Type.dispatch(int)
    assert isinstance(t, TypeType)
    assert t.type is int

    t = Type.dispatch((int, float))
    assert isinstance(t, MultiType)
    assert t.typelist == (int, float)

    t = Type.dispatch([1, 2])
    assert isinstance(t, ValuesType)
    assert t.values == [1, 2]
    
    t = Type.dispatch(six.string_types)
    assert isinstance(t, TypeType)
    t.validate('abc')
    t.validate(u'abc')
    assert_raises(TypeError, t.validate, 1)

    te = TypeExtension()
    assert Type.dispatch(te) is te
    assert Type.dispatch(TypeExtension) is not TypeExtension
    assert isinstance(Type.dispatch(TypeExtension), TypeExtension)

    assert_raises(TypeError, Type.dispatch, 1)
    assert_raises(TypeError, Type.dispatch, b'abc')
    assert_raises(TypeError, Type.dispatch, u'abc')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
