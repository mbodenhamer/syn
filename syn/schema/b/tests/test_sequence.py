from syn.schema.b import Sequence, Set, Or, Repeat, Optional, OneOrMore, \
    ZeroOrMore
from syn.sets import SetWrapper, TypeWrapper, Range

#-------------------------------------------------------------------------------
# Test conversion

def test_conversion():
    s = Sequence(1, 2, 3)
    assert list(s) == [Set(SetWrapper([1])), Set(SetWrapper([2])),
                       Set(SetWrapper([3]))]

    sw = SetWrapper([1, 2])
    s = Sequence(sw)
    assert list(s) == [Set(sw)]
    assert s[0].set is sw

    s = Sequence(Set(sw))
    assert list(s) == [Set(sw)]
    assert s[0].set is sw

    s = Sequence(int, float)
    assert list(s) == [Set(TypeWrapper(int)), Set(TypeWrapper(float))]

    s = Sequence({1, 2})
    assert list(s) == [Set(sw)]
    assert s[0].set == sw

    s = Sequence([1, 2])
    assert list(s) == [Set(sw)]
    assert s[0].set == sw

    o = Or(1, [2, 3])
    assert list(o) == [Set(SetWrapper([1])), Sequence(2, 3)]

#-------------------------------------------------------------------------------
# Test generation

def test_generation():
    s = Sequence(1, 2, 3)
    assert s.get_one() == [1, 2, 3]
    assert s.sample() == [1, 2, 3]
    assert list(s.enumerate()) == [[1, 2, 3]]

    s = Sequence(1, Repeat(2, lb=0, ub=3))
    assert sorted(s.enumerate()) == [[1],
                                     [1, 2],
                                     [1, 2, 2],
                                     [1, 2, 2, 2]]

    s = Sequence(Optional(1))
    assert sorted(s.enumerate()) == [[], [1]]

    s = Sequence(ZeroOrMore(1))
    assert sorted(s.enumerate()) == [[],
                                     [1],
                                     [1, 1],
                                     [1, 1, 1],
                                     [1, 1, 1, 1],
                                     [1, 1, 1, 1, 1]]

    s = Sequence(OneOrMore(1))
    assert sorted(s.enumerate()) == [[1],
                                     [1, 1],
                                     [1, 1, 1],
                                     [1, 1, 1, 1],
                                     [1, 1, 1, 1, 1],
                                     [1, 1, 1, 1, 1, 1]]

    s = Sequence(Or(1, [2, 3]))
    assert sorted(s.enumerate()) == [[1], [2, 3]]

    s = Sequence(Repeat(Or(1, 2), lb = 1, ub = 2), 5)
    assert sorted(s.enumerate()) == [[1, 1, 5],
                                     [1, 2, 5],
                                     [1, 5],
                                     [2, 1, 5],
                                     [2, 2, 5],
                                     [2, 5]]

    s = Sequence(Repeat(Repeat(1, lb=1, ub=2), lb=1, ub=2))
    assert sorted(s.enumerate()) == [[1],
                                     [1, 1],
                                     [1, 1, 1],
                                     [1, 1, 1],
                                     [1, 1, 1, 1]]

    s = Sequence(Or(2, Repeat(Repeat(1, lb=1, ub=2), lb=1, ub=2)), 3)
    assert sorted(s.enumerate()) == [[1, 1, 1, 1, 3],
                                     [1, 1, 1, 3],
                                     [1, 1, 1, 3],
                                     [1, 1, 3],
                                     [1, 3],
                                     [2, 3]]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
