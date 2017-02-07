from nose.tools import assert_raises
from syn.types.a import Type, Set, FrozenSet, \
    hashable, serialize, deserialize, estr, rstr, visit, find_ne, \
    SetDifferences, deep_feq, visit, safe_sorted
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent, on_error, elog, \
    ngzwarn, is_unique

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------

def examine_set(cls, val):
    assert type(val) is cls.type
    assert is_hashable(hashable(val))
    sval = deserialize(serialize(val))
    #assert deep_feq(sval, val)
    assert isinstance(rstr(val), str)

    assert list(visit(val)) == safe_sorted(list(val))
    assert find_ne(val, val) is None

    eitem = eval(estr(val))
    #assert deep_feq(eitem, val)
    assert type(eitem) is cls.type

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

    s1 = {1, 2, 3}
    s2 = {2, 3, 4}
    assert find_ne(s1, s2) == SetDifferences(s1, s2)

    examine_set(Set, set(s))
    examine_set(FrozenSet, s)

    # for cls in Set.__subclasses__():
    #     for k in xrange(SAMPLES):
    #         val = cls.generate()
    #         with on_error(elog, examine_set, (cls, val)):
    #             examine_set(cls, val)

    #     buf = []
    #     last = None
    #     for item in enumerate_(cls.type, max_enum=SAMPLES * 10, step=100):
    #         assert type(item) is cls.type
    #         assert item != last
    #         buf.append(item)
    #         last = item

    #     assert is_unique(buf)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
