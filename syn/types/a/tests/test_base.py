from nose.tools import assert_raises
from syn.five import xrange
from syn.types.a import Type, hashable, TYPE_REGISTRY, SER_KEYS, serialize, \
    deserialize, find_ne, DifferentTypes, safe_sorted, estr, find_ne, \
    generate, DiffersAtAttribute, hashable, rstr, visit, deep_feq, attrs
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
    
    assert_raises(NotImplementedError, t._find_ne, 0, None)
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

    __hash__ = None

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

    sval = deserialize(serialize(f))
    assert_equivalent(sval, f)
    assert deep_feq(sval, f)

    #assert_equivalent(Foo, deserialize(serialize(Foo)))

    val = generate(Foo)
    assert type(val) is Foo

    buf = []
    last = None
    for item in enum(Foo,  max_enum=SAMPLES * 10, step=100):
        assert type(item) is Foo
        assert item != last
        buf.append(item)
        last = item
        
    assert is_unique(buf)

    assert_equivalent(Foo(1, 2.3), Foo(1, 2.3))

#-------------------------------------------------------------------------------
# Test normal object with default type handler


class Bar(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b


def test_normal_type():

    # Because the types system knows nothing of the Bar class
    assert_raises(NotImplementedError, generate, Bar)
    assert_raises(NotImplementedError, list, enum(Bar, max_enum=50))

#-------------------------------------------------------------------------------
# Test object with special Type handler


class Baz(object):
    pass


def test_custom_type():
    pass

#-------------------------------------------------------------------------------
# safe_sorted

def test_safe_sorted():
    assert safe_sorted([2, 1]) == [1, 2]
    safe_sorted(['abc', 1, 1.2])

    l = [False, u'\U0007d6a8\U000eae9f\U0006f152\U0002e17b\U000fee84\ue5e3\U0003cb54\U0009714f\U00086b2e\U0004f0fb\U000b6252\U0010b9a3\U000efeed\U000c2391\U00102ba0\U000331fa\U00092fcc\U000bc6d1\U000814cd\U000e0d19', u'\U0002875e\U000cdb29\U000dc70a\U0010671d\U0004194e\U0007516e\U000ff0b7\U000a2e49\U0004d60f\U000e1499\U000953ae\U000abb2f\U0002fbf6\U000f0fe5\U00100071\U00066d73\U000a8bd3\U0009c37c\U000efdea\U000a98be\U000b271d\U000c501c\U0010aa46\U0009b7be\U00024745\U0007622c\U000a39d9\U0010b7f2\U000eec1d\U000b089e\U0002defa\u3db9\U00078d12\U0003105e\U0007db13\U0008f032\U0001211d\U000de037\U0005a373\U0005a1a4\U000a9593\U000d3db3\U00094ad7\U000ec0ae\U0003b8cf\U0008c42c\U0002c535\u50db\U00010148\U000bbd7f\U000b5def\udfe0\U000d3cb6\U0007b598\U0009c9ae\U000b496d\U0005a099\u4a0f\U000c1557\U000ae3f0\U000fd090\U0002d19d\U00103228\U0001691f\u34a7\U000f43e0\U0004a684', '\xee\x9eT\xb0\xcd\xf4\xc7\xf6x\xb2\x01(\xaf&\xd1C3\xe3t\xa4E\xe7f\xe6\xf4\xea\xd0Z\x07\xe8/\x90S"\xd5\xfc8\x88XY)\xefy\xe6\xeeM']
    safe_sorted(l)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
