from six import PY2
from nose.tools import assert_raises
from syn.types.a import Type, Mapping, Dict, \
    hashable, serialize, deserialize, estr, rstr, visit, find_ne
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent, on_error, elog, \
    ngzwarn, is_unique

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------

def examine_mapping(cls, val):
    assert type(val) is cls.type
    assert is_hashable(hashable(val))
    # sval = serialize(val)
    # import ipdb; ipdb.set_trace()
    # deserialize(sval)
    assert deserialize(serialize(val)) == val
    assert isinstance(rstr(val), str)

    assert list(visit(val)) == list(val.items())
    assert find_ne(val, val) is None

    eitem = eval(estr(val))
    assert eitem == val
    assert type(eitem) is cls.type

#-------------------------------------------------------------------------------
# Mapping

def test_mapping():
    d = dict(a = 1, b = 2.3)
    t = Type.dispatch(d)
    assert isinstance(t, Mapping)
    assert type(t) is Dict
    if PY2:
        assert set(hashable(d)) == set(t.hashable()) == \
            {'__builtin__.dict', ('a', 1), ('b', 2.3)}
    else:
        assert set(hashable(d)) == set(t.hashable()) == \
            {'builtins.dict', ('a', 1), ('b', 2.3)}

    assert not is_hashable(d)
    assert is_hashable(hashable(d))
    examine_mapping(Dict, d)

    # for cls in Mapping.__subclasses__():
    #     for k in xrange(SAMPLES):
    #         val = cls.generate()
    #         with on_error(elog, examine_mapping, (cls, val)):
    #             examine_mapping(cls, val)

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
