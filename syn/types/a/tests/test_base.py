import collections
from nose.tools import assert_raises
from syn.five import PY3
from syn.types.a import Type, hashable, TYPE_REGISTRY, SER_KEYS, serialize, \
    deserialize, DifferentTypes, safe_sorted, estr, find_ne, \
    generate, DiffersAtAttribute, rstr, visit, deep_feq, attrs, \
    NotEqual, pairs, enumeration_value, primitive_form, collect
from syn.types.a import enumerate as enum
from syn.base_utils import get_fullname, is_hashable, assert_inequivalent, \
    assert_equivalent, first, get_typename, ngzwarn, is_unique

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------
# Type

def test_type():
    t = Type(1)
    assert t.obj == 1
    assert t.rstr() == '1'
    assert t.hashable() is t.obj

    class Foo(object):
        __hash__ = None

    f = Foo()
    f.a = 1

    g = Foo()
    g.a = 2

    assert not is_hashable(f)
    assert is_hashable(hashable(f))
    assert_inequivalent(hashable(f), hashable(g))

    dct = serialize(f)
    assert dct[SER_KEYS.attrs]['a'] == 1
    
    assert t.find_ne(0) == NotEqual(1, 0)
    assert list(t.visit(0)) == [1]
    assert t.visit_len() == 1

    t = Type.type_dispatch(Foo)
    assert_raises(NotImplementedError, t._enumeration_value, 1)
    assert_raises(NotImplementedError, t._generate)

    assert TYPE_REGISTRY[object] is Type

    assert isinstance(find_ne(1, 1.2), DifferentTypes)

#-------------------------------------------------------------------------------
# Test object with defined special methods


class Foo(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.a == other.a and
                self.b == other.b)

    def __ne__(self, other):
        return not self == other

    __hash__ = None

    def _collect(self, func, **kwargs):
        return func(dict(a = collect(self.a, **kwargs),
                         b = collect(self.b, **kwargs)),
                    **kwargs)

    def _primitive_form(self, **kwargs):
        return dict(a = primitive_form(self.a, **kwargs),
                    b = primitive_form(self.b, **kwargs))

    def _deserialize(self, dct):
        # Do something useful here
        pass

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        a = first(enum(int, start=x, max_enum=1))
        b = first(enum(float, start=x, max_enum=1))
        return cls(a, b)

    def _estr(self, **kwargs):
        a = estr(self.a, **kwargs)
        b = estr(self.b, **kwargs)
        return '{}({},{})'.format(get_typename(self), a, b)

    def _find_ne(self, other, func, **kwargs):
        if not func(self.a, other.a):
            return DiffersAtAttribute(self, other, 'a')
        if not func(self.b, other.b):
            return DiffersAtAttribute(self, other, 'b')

    @classmethod
    def _generate(cls, **kwargs):
        a = generate(int, **kwargs)
        b = generate(float, **kwargs)
        return cls(a, b)

    def _hashable(self, **kwargs):
        return (get_fullname(self), hashable(self.a), hashable(self.b))

    def _rstr(self, **kwargs):
        a = rstr(self.a, **kwargs)
        b = rstr(self.b, **kwargs)
        return '{}({},{})'.format(get_typename(self), a, b)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [serialize(self.a, **kwargs),
                              serialize(self.b, **kwargs)]
        return dct

    def _visit(self, k, **kwargs):
        if k == 0:
            return 'a', self.a
        return 'b', self.b

    def _visit_len(self, **kwargs):
        return 2

class FooType(Type): type = Foo


def test_custom_object():
    f = Foo(1, 1.2)
    f2 = Foo(1, 1.3)
    f3 = Foo(2, 1.2)

    assert f != f2
    assert_equivalent(Foo(1, 2.3), Foo(1, 2.3))

    assert not is_hashable(f)
    assert is_hashable(hashable(f))

    assert find_ne(f, f) is None
    assert find_ne(f, f2) == DiffersAtAttribute(f, f2, 'b')
    assert find_ne(f, f3) == DiffersAtAttribute(f, f3, 'a')

    e1 = eval(estr(f))
    assert_equivalent(e1, f)

    assert list(visit(f)) == [('a', 1), ('b', 1.2)]
    assert rstr(f) == 'Foo(1,1.2)'

    assert attrs(f) == ['a', 'b']
    assert pairs(f) == [('a', 1), ('b', 1.2)]

    sval = deserialize(serialize(f))
    assert_equivalent(sval, f)
    assert deep_feq(sval, f)

    assert Foo is deserialize(serialize(Foo))
    assert primitive_form(Foo) is Foo
    assert primitive_form(f) == dict(a=1, b=1.2)
    assert collect(f) == primitive_form(f)

    val = generate(Foo)
    assert type(val) is Foo

    buf = []
    last = None
    for item in enum(Foo,  max_enum=SAMPLES * 10, step=100):
        assert type(item) is Foo
        assert item != last
        buf.append(item)
        last = item

    assert enumeration_value(Foo, 0) == first(enum(Foo, max_enum=1))
    assert is_unique(buf)

#-------------------------------------------------------------------------------
# Test normal object with default type handler


class Bar(object):
    def __init__(self, a=None, b=None):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.a == other.a and
                self.b == other.b)

    def __ne__(self, other):
        return not self == other


def test_normal_type():
    b = Bar(1, 2.3)
    b2 = Bar(1, 2.4)
    b3 = Bar(2, 2.3)

    assert b != b2
    assert_equivalent(Bar(1, 2.3), Bar(1, 2.3))

    if PY3:
        assert not is_hashable(b)
    else:
        assert is_hashable(b)
    assert is_hashable(hashable(b))

    assert find_ne(b, b) is None
    assert find_ne(b, b2) == DiffersAtAttribute(b, b2, 'b')
    assert find_ne(b, b3) == DiffersAtAttribute(b, b3, 'a')

    # Is evaluable, but not correct, because we haven't given the
    # types system the proper information for this class
    e1 = eval(estr(b))
    assert b != e1

    assert list(visit(b)) == [('a', 1), ('b', 2.3)]
    assert attrs(b) == ['a', 'b']
    assert rstr(b).startswith('<{} object at '.format(get_fullname(Bar)))

    sval =  deserialize(serialize(b))
    assert_equivalent(b, sval)
    assert deep_feq(b, sval)

    assert primitive_form(Bar) is Bar
    assert primitive_form(b) == dict(a=1, b=2.3)

    b4 = Bar(2, b2)
    assert primitive_form(b4) == dict(a=2, b=dict(a=1, b=2.4))

    assert collect(b4) == primitive_form(b4)
    
    def dothing(obj):
        if isinstance(obj, collections.Mapping):
            return safe_sorted(obj.values())
        return safe_sorted(obj)
    assert collect(b4, dothing) in [[2, [1, 2.4]],
                                    [2, [2.4, 1]],
                                    [[1, 2.4], 2],
                                    [[2.4, 1], 2]]

    # Because the types system knows nothing of the Bar class
    assert_raises(NotImplementedError, generate, Bar)
    assert_raises(NotImplementedError, list, enum(Bar, max_enum=50))

#-------------------------------------------------------------------------------
# Test object with special Type handler


class Baz(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.a == other.a and
                self.b == other.b)

    def __ne__(self, other):
        return not self == other


class BazType(Type):
    type = Baz
    gen_types = (int, float)
    ser_args = ('a', 'b')

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        a = first(enum(int, start=x, max_enum=1))
        b = first(enum(float, start=x, max_enum=1))
        return cls.type(a, b)

    def estr(self, **kwargs):
        return '{}({},{})'.format(get_typename(self.obj), 
                                  estr(self.obj.a),
                                  estr(self.obj.b))

    def _rstr(self, **kwargs):
        return '{}({},{})'.format(get_typename(self.obj), 
                                  rstr(self.obj.a),
                                  rstr(self.obj.b))


def test_custom_type():
    b = Baz(1, 2.3)
    b2 = Baz(1, 2.4)
    b3 = Baz(2, 2.3)

    assert b != b2
    assert_equivalent(Baz(1, 2.3), Baz(1, 2.3))

    if PY3:
        assert not is_hashable(b)
    else:
        assert is_hashable(b)
    assert is_hashable(hashable(b))

    assert find_ne(b, b) is None
    assert find_ne(b, b2) == DiffersAtAttribute(b, b2, 'b')
    assert find_ne(b, b3) == DiffersAtAttribute(b, b3, 'a')

    e1 = eval(estr(b))
    assert_equivalent(e1, b)

    assert list(visit(b)) == [('a', 1), ('b', 2.3)]
    assert rstr(b) == 'Baz(1,2.3)'

    assert attrs(b) == ['a', 'b']

    sval = deserialize(serialize(b))
    assert_equivalent(sval, b)
    assert deep_feq(sval, b)

    assert Baz is deserialize(serialize(Baz))
    assert primitive_form(Baz) is Baz
    assert primitive_form(b) == dict(a=1, b=2.3)

    val = generate(Baz)
    assert type(val) is Baz
    assert isinstance(val.a, int)
    assert isinstance(val.b, float)

    buf = []
    last = None
    for item in enum(Baz,  max_enum=SAMPLES * 10, step=100):
        assert type(item) is Baz
        assert item != last
        buf.append(item)
        last = item
        
    assert is_unique(buf)

#-------------------------------------------------------------------------------
# Misc. Serializaation


class KWObject(object):
    def __init__(self, **kwargs):
        self.a = kwargs['a']
        self.b = kwargs['b']

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.a == other.a and
                self.b == other.b)

    def __ne__(self, other):
        return not self == other

class KWObjectType(Type):
    type = KWObject
    ser_kwargs = ['a', 'b']


class Foo2(object):
    def __init__(self, a, **kwargs):
        self.a = a
        setattr(self, ':b', kwargs['b'])
        setattr(self, 'c-1', kwargs['c'])

    def __eq__(self, other):
        return (type(self) is type(other) and
                self.a == other.a and
                getattr(self, ':b') == getattr(other, ':b') and
                getattr(self, 'c-1') == getattr(other, 'c-1'))

    def __ne__(self, other):
        return not self == other

class Foo2Type(Type):
    type = Foo2
    ser_args = ['a']
    ser_kwargs = ['b', 'c']
    ser_kwargmap = dict(b = ':b',
                        c = 'c-1')


class NoSer(object):
    pass

class NoSerType(Type):
    type = NoSer
    ser_attrs = False


def test_misc_serialization():
    assert int is deserialize(serialize(int))

    d = dict(a=1, b=2)
    dd = deserialize(d)
    assert_equivalent(d, dd)

    k = KWObject(a=1, b=2.3)
    assert k != KWObject(a=2, b=2.3)
    assert_equivalent(KWObject(a=1, b=2.3), KWObject(b=2.3, a=1))
    
    sval = deserialize(serialize(k))
    assert_equivalent(sval, k)
    assert deep_feq(sval, k)
    assert KWObject is deserialize(serialize(KWObject))

    f = Foo2(1, b=2.3, c='abc')
    f2 = Foo2(1, b=2.4, c='abc')
    assert f != f2

    sval = deserialize(serialize(f))
    assert_equivalent(sval, f)
    assert deep_feq(sval, f)
    assert Foo2 is deserialize(serialize(Foo2))

    n = NoSer()
    n.a = 1

    sval = deserialize(serialize(n))
    assert isinstance(sval, NoSer)
    assert n != sval
    assert vars(n) != vars(sval)
    assert n.a == 1
    assert not hasattr(sval, 'a')

#-------------------------------------------------------------------------------
# misc


class DictWrapper(object):
    def __init__(self, dct):
        self.dct = dct

class DictWrapperType(Type):
    type = DictWrapper
    gen_type = dict


def test_misc():
    w = generate(DictWrapper)
    assert isinstance(w, DictWrapper)
    assert isinstance(w.dct, dict)

#-------------------------------------------------------------------------------
# safe_sorted

def test_safe_sorted():
    assert safe_sorted(1) == 1
    assert safe_sorted([2, 1]) == [1, 2]
    safe_sorted(['abc', 1, 1.2])

    l = [False, u'\U0007d6a8\U000eae9f\U0006f152\U0002e17b\U000fee84\ue5e3\U0003cb54\U0009714f\U00086b2e\U0004f0fb\U000b6252\U0010b9a3\U000efeed\U000c2391\U00102ba0\U000331fa\U00092fcc\U000bc6d1\U000814cd\U000e0d19', u'\U0002875e\U000cdb29\U000dc70a\U0010671d\U0004194e\U0007516e\U000ff0b7\U000a2e49\U0004d60f\U000e1499\U000953ae\U000abb2f\U0002fbf6\U000f0fe5\U00100071\U00066d73\U000a8bd3\U0009c37c\U000efdea\U000a98be\U000b271d\U000c501c\U0010aa46\U0009b7be\U00024745\U0007622c\U000a39d9\U0010b7f2\U000eec1d\U000b089e\U0002defa\u3db9\U00078d12\U0003105e\U0007db13\U0008f032\U0001211d\U000de037\U0005a373\U0005a1a4\U000a9593\U000d3db3\U00094ad7\U000ec0ae\U0003b8cf\U0008c42c\U0002c535\u50db\U00010148\U000bbd7f\U000b5def\udfe0\U000d3cb6\U0007b598\U0009c9ae\U000b496d\U0005a099\u4a0f\U000c1557\U000ae3f0\U000fd090\U0002d19d\U00103228\U0001691f\u34a7\U000f43e0\U0004a684', '\xee\x9eT\xb0\xcd\xf4\xc7\xf6x\xb2\x01(\xaf&\xd1C3\xe3t\xa4E\xe7f\xe6\xf4\xea\xd0Z\x07\xe8/\x90S"\xd5\xfc8\x88XY)\xefy\xe6\xeeM']
    safe_sorted(l)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
