from nose.tools import assert_raises
from syn.types.a import Type, hashable, TYPE_REGISTRY, SER_KEYS, serialize, \
    deserialize, find_ne
from syn.types.a.ne import Value
from syn.base_utils import get_fullname, is_hashable, assert_inequivalent

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
    

    t = Type.type_dispatch(Foo)
    assert_raises(NotImplementedError, t._enumeration_value, 1)
    assert_raises(NotImplementedError, t._generate)

    assert TYPE_REGISTRY[object] is Type


    assert find_ne(1, 1.2) == Value("different types ({} =/= {})"
                                    .format(int, float))

#-------------------------------------------------------------------------------
# Test object with defined methods

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
