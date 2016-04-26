from nose.tools import assert_raises
from syn.type.a.ext import (Callable, List, Sequence, Mapping, Dict, Hashable,
                            Tuple, AssocList)

#-------------------------------------------------------------------------------
# Callable

def test_callable():
    class Foo(object):
        def __call__(self):
            pass

    Foo()()
    t = Callable()
    t.check(Foo())
    t.check(test_callable)
    t.check(int)
    t.validate(int)
    assert_raises(TypeError, t.check, 1)
    assert_raises(TypeError, t.validate, 1)

#-------------------------------------------------------------------------------
# Hashable

def test_hashable():
    t = Hashable()
    assert t.query(3)
    assert not t.query(dict(a = 3))

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    int_seq = Sequence(int)

    assert int_seq.query([1, 2, 3])
    assert not int_seq.query([1.2, 2, 3])
    assert int_seq.query((1, 2, 3))
    assert not int_seq.query(1)

    int_list = List(int)

    assert int_list.query([1, 2, 3])
    assert not int_list.query([1.2, 2, 3])
    assert not int_list.query((1, 2, 3))

    bad_list = (1.2, '3', 4)
    good_list = [1, 2, 3]
    assert int_list.coerce(bad_list) == [1, 3, 4]
    assert int_list.coerce(good_list) is good_list

#-------------------------------------------------------------------------------
# Tuple

def test_tuple():
    t = Tuple(int)
    assert t.types.type is int
    assert t.uniform
    assert t.length is None

    assert t.query((1, 2, 3))
    assert t.query((1,))
    assert not t.query([1, 2])
    assert not t.query((1, 2.3, 3))
    assert t.coerce([1, 2.3, '3']) == (1, 2, 3)

    t = Tuple(int, 2)
    assert t.types.type is int
    assert t.uniform
    assert t.length == 2

    assert t.query((1, 2))
    assert not t.query((1, 2.3))
    assert not t.query((1, 2, 3))
    assert t.coerce((1, 2)) == (1, 2)
    assert t.coerce([1.2, '2']) == (1, 2)
    assert_raises(TypeError, t.coerce, [1, 2.3, '3'])

    t = Tuple((int, float))
    assert not t.uniform
    assert t.length == 2

    assert t.query((1, 2.3))
    assert not t.query((2.3, 1))
    assert t.coerce((2.3, 1)) == (2, 1.0)

    t = Tuple((int, float), uniform=True)
    assert t.uniform
    assert t.length is None

    assert t.query((2.3, 2.3))
    assert t.query((1, 1))
    assert t.query((2.3, 1))
    assert not t.query(('abc', 1))

#-------------------------------------------------------------------------------
# AssocList

def test_assoclist():
    t = AssocList
    assert t.query([('a', 2), ('b', 3)])
    assert not t.query([('a', 2), ('b', 3, 4)])

#-------------------------------------------------------------------------------
# Mapping

def test_mapping():
    int_map = Mapping(int)

    assert int_map.query(dict(a=1, b=2))
    assert not int_map.query(dict(a=1.2, b=2))
    assert not int_map.query(1)

    int_dict = Dict(int)
    assert int_dict.query(dict(a=1, b=2))
    assert not int_dict.query(dict(a=1.2, b=2))
    assert not int_dict.query(1)

    bad_dict = dict(a=1.2, b='3', c=4)
    good_dict = dict(a=1, b=2, c=3)
    assert int_dict.coerce(bad_dict) == dict(a=1, b=3, c=4)
    assert int_dict.coerce(good_dict) is good_dict

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
