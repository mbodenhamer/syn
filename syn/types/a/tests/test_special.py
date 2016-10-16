from syn.types.a import Type, NONE, \
    hashable, serialize, deserialize, estr, rstr
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent

#-------------------------------------------------------------------------------
# None

def test_none():
    n = None
    t = Type.dispatch(n)
    assert isinstance(t, NONE)
    assert type(t) is NONE

    assert hashable(n) is t.hashable() is n
    assert is_hashable(n)
    assert is_hashable(hashable(n))
    assert deserialize(serialize(n)) is n

    val = NONE.generate()
    assert val is None
    assert rstr(n) == 'None'
    assert eval(estr(n)) is n

    for item in enumerate_(type(None), max_enum=1):
        assert item is None

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
