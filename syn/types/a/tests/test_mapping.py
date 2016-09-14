from six import PY2
from nose.tools import assert_raises
from syn.types.a import Type, Mapping, Dict, \
    hashable, serialize, deserialize, estr, rstr, enumerate_
from syn.base_utils import is_hashable, assert_equivalent

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

    for cls in Mapping.__subclasses__():
        val = cls.generate()
        assert type(val) is cls.type
        # assert is_hashable(hashable(val))
        # assert_equivalent(deserialize(serialize(val)), val)
    
        assert isinstance(rstr(val), str)
        # assert_equivalent(eval(estr(val)), val)

        # for item in enumerate_(cls, max_enum=1):
        #     assert type(item) is cls.type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
