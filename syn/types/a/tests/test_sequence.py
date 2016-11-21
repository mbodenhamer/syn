from six import PY2
from syn.five import xrange
from nose.tools import assert_raises
from syn.types.a import Type, Sequence, List, Tuple, \
    hashable, serialize, deserialize, estr, rstr, visit, find_ne, \
    DifferentLength, DiffersAtIndex
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent, elog, ngzwarn, \
    is_unique, on_error

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------

def examine_sequence(cls, val):
    assert type(val) is cls.type
    assert is_hashable(hashable(val))
    assert deserialize(serialize(val)) == val
    assert isinstance(rstr(val), str)

    assert list(visit(val)) == list(val)
    assert find_ne(val, val) is None

    eitem = eval(estr(val))
    assert eitem == val
    assert type(eitem) is cls.type

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    l = [1, 2.3, 'abc']
    t = Type.dispatch(l)
    assert isinstance(t, Sequence)
    assert type(t) is List
    if PY2:
        assert set(hashable(l)) == set(t.hashable()) == \
            {'__builtin__.list', 1, 2.3, 'abc'}
    else:
        assert set(hashable(l)) == set(t.hashable()) == \
            {'builtins.list', 1, 2.3, 'abc'}

    assert not is_hashable(l)
    assert is_hashable(hashable(l))

    l1 = [1, 2, 3]
    l2 = [1, 2, 3, 4]
    l3 = [1, 2, 4]
    assert find_ne(l1, l2) == DifferentLength(l1, l2)
    assert find_ne(l2, l1) == DifferentLength(l2, l1)
    assert find_ne(l1, l3) == DiffersAtIndex(l1, l3, 2)

    tup = tuple(l)
    examine_sequence(List, l)
    examine_sequence(Tuple, tup)
    
    # for cls in Sequence.__subclasses__():
    #     for k in xrange(SAMPLES):
    #         val = cls.generate()
    #         with on_error(elog, examine_sequence, (cls, val)):
    #             examine_sequence(cls, val)

    #     buf = []
    #     last = None
    #     for item in enumerate_(cls.type, max_enum=SAMPLES * 10, step=100):
    #         assert type(item) is cls.type
    #         assert item != last
    #         buf.append(item)
    #         last = item

    #     assert is_unique(buf)

    assert list(visit(l, enumerate=True)) == [(0, 1), (1, 2.3), (2, 'abc')]
    assert list(visit([])) == []

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
