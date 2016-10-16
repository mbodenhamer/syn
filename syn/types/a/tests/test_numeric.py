from six import PY2
from syn.types.a import Type, Numeric, Int, hashable, rstr, serialize, \
    deserialize, estr, generate, TYPE_REGISTRY, Long
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, collection_comp, assert_equivalent, \
    feq, assert_type_equivalent

#-------------------------------------------------------------------------------
# Numeric

def test_numeric():
    x = 1
    t = Type.dispatch(x)
    assert isinstance(t, Numeric)
    assert type(t) is Int

    assert hashable(x) == x

    for cls in Numeric.__subclasses__():
        if cls.type is None:
            continue

        val = cls.generate()
        assert type(val) is cls.type
        assert is_hashable(hashable(val))
        assert deserialize(serialize(val)) == val
        assert isinstance(rstr(val), str)

        for item in enumerate_(cls.type, max_enum=1):
            assert type(item) is cls.type

            eitem = eval(estr(item))
            assert eitem == item
            assert type(eitem) is cls.type

#-------------------------------------------------------------------------------
# Bool

def test_bool():
    lst = list(enumerate_(bool, max_enum=5))
    assert lst == [False, True, False, True, False]

    lst = list(enumerate_(bool, max_enum=5, start=1))
    assert lst == [True, False, True, False, True]

    assert rstr(True) == estr(True) == 'True'
    assert hashable(False) is False

    gen = generate(bool)
    assert gen is True or gen is False

    assert serialize(True) is True
    assert deserialize(True) is True

#-------------------------------------------------------------------------------
# Int

def test_int():
    lst = list(enumerate_(int, max_enum=5))
    assert lst == [0, 1, 2, 3, 4]

    lst = list(enumerate_(int, max_enum=5, start=1, step=3))
    assert lst == [1, 4, 7, 10, 13]

    assert rstr(1) == estr(1) == '1'
    assert hashable(-1) == -1

    gen = generate(int)
    assert isinstance(gen, int)

    assert serialize(-1) == -1
    assert deserialize(-1) == -1

#-------------------------------------------------------------------------------
# Long

def test_long():
    if PY2:
        lst = list(enumerate_(long, max_enum=5))
        assert lst == [0, 1, 2, 3, 4]
        
        x = long('1L')
        assert rstr(x) == '1'
        assert estr(x) == '1L'
        assert_equivalent(hashable(-x), -x)

        gen = generate(long)
        assert isinstance(gen, long)

        assert_type_equivalent(deserialize(serialize(x)), x)

        assert TYPE_REGISTRY[long] is Long
        assert Long in TYPE_REGISTRY.values()
    else:
        assert Long not in TYPE_REGISTRY.values()

#-------------------------------------------------------------------------------
# Float

def test_float():
    lst = list(enumerate_(float, max_enum=5))
    assert collection_comp(lst, [0.0, 0.1, 0.2, 0.3, 0.4], feq)

    lst = list(enumerate_(float, max_enum=3, start=1, step=3, float_step=.2))
    assert collection_comp(lst, [0.2, 0.8, 1.4], feq)

    assert rstr(1.1) == estr(1.1) == '1.1'
    assert hashable(1.1) == 1.1

    gen = generate(float)
    assert isinstance(gen, float)

    assert serialize(-1.1) == -1.1
    assert deserialize(-1.1) == -1.1

#-------------------------------------------------------------------------------
# Complex

def test_complex():
    lst = list(enumerate_(complex, max_enum=3))
    assert collection_comp(lst, [0+0j, 0.1+0.05j, 0.2+0.1j], feq)

    c = 1+2j
    assert rstr(c) == estr(c) == '(1+2j)'
    assert eval(estr(c)) == c

    assert hashable(c) is c

    gen = generate(complex)
    assert isinstance(gen, complex)

    assert_type_equivalent(deserialize(serialize(c)), c)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)