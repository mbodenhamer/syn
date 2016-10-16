from nose.tools import assert_raises
from syn.types.a import Type, Set, FrozenSet, \
    hashable, serialize, deserialize, estr, rstr
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent

#-------------------------------------------------------------------------------
# Set

def test_set():
    s = frozenset([1, 2.3, 'abc'])
    t = Type.dispatch(s)
    assert isinstance(t, Set)
    assert type(t) is FrozenSet

    assert hashable(s) == t.hashable() == s
    assert is_hashable(s)
    assert is_hashable(hashable(s))

    for cls in Set.__subclasses__():
        val = cls.generate()
        assert type(val) is cls.type
        assert is_hashable(hashable(val))
        #assert_equivalent(deserialize(serialize(val)), val)
    
        assert isinstance(rstr(val), str)
        # assert_equivalent(eval(estr(val)), val)

        # for item in enumerate_(cls, max_enum=1):
        #     assert type(item) is cls.type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
