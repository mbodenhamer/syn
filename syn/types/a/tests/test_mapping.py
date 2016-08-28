from nose.tools import assert_raises
from syn.types.a import Type, Mapping, Dict, hashable
from syn.base_utils import is_hashable

#-------------------------------------------------------------------------------
# Mapping

def test_mapping():
    d = dict(a = 1, b = 2.3)
    t = Type.dispatch(d)
    assert isinstance(t, Mapping)
    assert type(t) is Dict
    assert sorted(hashable(d)) == sorted(t.hashable()) == [('a', 1), ('b', 2.3)]

    assert not is_hashable(d)
    assert is_hashable(hashable(d))

    for cls in Mapping.__subclasses__():
        val = cls.generate()
        assert type(val) is cls.type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
