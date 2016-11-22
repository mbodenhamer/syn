from syn.types.a import Type, NONE, \
    hashable, serialize, deserialize, estr, rstr, visit, find_ne, DifferentTypes
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable

#-------------------------------------------------------------------------------
# None

def test_none():
    n = None
    t = Type.dispatch(n)
    assert isinstance(t, NONE)
    assert type(t) is NONE

    assert t._find_ne(None, None) is None
    assert t._find_ne(1, None) is None

    assert hashable(n) is t.hashable() is n
    assert is_hashable(n)
    assert is_hashable(hashable(n))
    assert deserialize(serialize(n)) is n

    val = NONE.generate()
    assert val is None
    assert rstr(n) == 'None'
    assert eval(estr(n)) is n

    for item in enumerate_(type(None), max_enum=10):
        assert item is None

    assert list(visit(None)) == [None]
    assert find_ne(None, None) is None
    assert isinstance(find_ne(None, 1), DifferentTypes)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
