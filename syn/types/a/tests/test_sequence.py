from six import PY2
from nose.tools import assert_raises
from syn.types.a import Type, Sequence, List, Tuple, \
    hashable, serialize, deserialize, estr, rstr
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent

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

    for cls in Sequence.__subclasses__():
        val = cls.generate()
        assert type(val) is cls.type
        assert is_hashable(hashable(val))
        # assert_equivalent(deserialize(serialize(val)), val)
    
        assert isinstance(rstr(val), str)
        # assert_equivalent(eval(estr(val)), val)

        # for item in enumerate_(cls, max_enum=1):
        #     assert type(item) is cls.type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
