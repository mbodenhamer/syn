from syn.types.a import Type, Numeric, Int, hashable, rstr, serialize, \
    deserialize
from syn.base_utils import is_hashable, assert_equivalent

#-------------------------------------------------------------------------------
# Numeric

def test_numeric():
    x = 1
    t = Type.dispatch(x)
    assert isinstance(t, Numeric)
    assert type(t) is Int

    assert hashable(x) == x

    for cls in Numeric.__subclasses__():
        val = cls.generate()
        assert type(val) is cls.type
        assert is_hashable(hashable(val))
        assert deserialize(serialize(val)) == val
    
        assert isinstance(rstr(val), str)
        # assert_equivalent(eval(estr(val)), val)

        # for item in enumerate_(cls, max_enum=1):
        #     assert type(item) is cls.type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
