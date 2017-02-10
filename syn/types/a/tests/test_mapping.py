from six import PY2
from syn.five import xrange
from nose.tools import assert_raises
from syn.types.a import Type, Mapping, Dict, \
    hashable, serialize, deserialize, estr, rstr, visit, find_ne, \
    DiffersAtKey, KeyDifferences, deep_feq, safe_sorted
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent, on_error, elog, \
    ngzwarn, is_unique, subclasses, hangwatch

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------

def examine_mapping(cls, val):
    assert type(val) is cls.type
    assert is_hashable(hashable(val))
    sval = deserialize(serialize(val))
    assert deep_feq(sval, val)
    assert isinstance(rstr(val), str)

    assert list(visit(val)) == safe_sorted(list(val.items()))
    assert find_ne(val, val) is None

    # NOTE: estr has been relegated to experimental status for now
    # eitem = eval(estr(val))
    # assert deep_feq(sval, val)
    # assert type(eitem) is cls.type

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

    d1 = dict(a=1, b=2)
    d2 = dict(a=1, b=2, c=3)
    d3 = dict(a=1, b=3)
    assert find_ne(d1, d2) == KeyDifferences(d1, d2)
    assert find_ne(d2, d1) == KeyDifferences(d2, d1)
    assert find_ne(d1, d3) == DiffersAtKey(d1, d3, 'b')

    e1 = eval(estr(d1))
    assert_equivalent(e1, d1)

    assert not is_hashable(d)
    assert is_hashable(hashable(d))
    examine_mapping(Dict, d)


    for cls in subclasses(Mapping):
        for k in xrange(SAMPLES):
            val = cls.generate()
            with on_error(elog, examine_mapping, (cls, val)):
                hangwatch(1, examine_mapping, cls, val)

        buf = []
        last = None
        for item in enumerate_(cls.type, max_enum=SAMPLES * 10, step=100):
            assert type(item) is cls.type
            assert item != last
            buf.append(item)
            last = item

        assert is_unique(buf)

#-------------------------------------------------------------------------------
# Bad test cases

# def test_bad_cases():
#     from syn.types.a import OrderedDict as OrderedDict_
#     from collections import OrderedDict

#     val = OrderedDict([((-1.4295764407292497e+308+1.424986100748943e+308j), 
#                         -810127967009107279), 
#                        (-1.827012095486929e+307, None), 
#                        (1.6642652599670256e+308, 
#                         {8.938423188190213e+307: False, 
#                          (1.0761629010589936e+308-1.6057678269394774e+308j): False}), 
#                        (1321286071298621711, (-1.1971920347818657e+308-7.047893113499448e+307j))])
#     examine_mapping(OrderedDict_, val)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
