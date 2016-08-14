from nose.tools import assert_raises
from syn.five import STR
from syn.schema.b.sequence import Sequence, Set, Or, Repeat, Optional, \
    OneOrMore, ZeroOrMore, MatchFailure, MatchFailed, Match, Type
from syn.sets import SetWrapper, TypeWrapper, Range
from syn.base_utils import IterableList

#-------------------------------------------------------------------------------
# Match

def test_match():
    m = Match()
    assert m

    m = Match(*[1, 2, 3])
    assert list(m) == [1, 2, 3]

#-------------------------------------------------------------------------------
# MatchFailure

def test_matchfailure():
    m = MatchFailure(message='abc', seq=IterableList([]))
    assert not m

#-------------------------------------------------------------------------------
# MatchFailed

def test_matchfailed():
    msg = 'abc'
    seq = IterableList([])

    e = MatchFailed(msg, seq)
    assert e.fails == []
    assert e.failure() == MatchFailure(message=msg, seq=seq, fails=[])

    def ex():
        raise e

    assert_raises(Exception, ex)    
    assert_raises(MatchFailed, ex)    

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
    assert list(o) == [Set(SetWrapper([1])), Set(SetWrapper([2, 3]))]

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
    assert sorted(s.enumerate()) == [[1], [2], [3]]

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
# Test Matching

def test_matching():
    s = Sequence('a', 'b', 'c')

    assert s.match('abc')
    assert list(s.match('abc')) == ['a', 'b', 'c']

    f = s.match('d')
    assert f.message == 'Item not in set'
    assert f.seq.position == 0

    f = s.match('')
    assert f.message == 'Sequence is too short'
    assert f.seq.position == 0

    s = Sequence(Or('a', 'b'))
    assert s.match('a')
    assert s.match('b')
    assert not s.match('c')
    assert s.match('ac')
    assert not s.match('ac', strict=True)

    f = s.match('c')
    assert f.message == 'Did not meet any Or conditions'
    assert f.seq.position == 0
    assert f.fails[0].message == 'Item not in set'
    assert f.fails[0].seq.position == 0

    f = s.match('ac', strict=True)
    assert f.message == 'Sequence is too long'
    assert f.seq.position == 1

    s = Sequence(OneOrMore('a'))
    assert not s.match('')
    assert s.match('a')
    assert s.match('a' * 50)
    assert not s.match('ab', strict=True)

    f = s.match('')
    assert f.message == 'Did not match enough repetitions'
    assert f.seq.position == 0
    assert f.fails[0].message == 'Sequence is too short'
    assert f.fails[0].seq.position == 0

    s = Sequence(Repeat(Or('a', 'b'), lb=1, ub=3))
    assert not s.match('')
    assert s.match('a')
    assert s.match('b')
    assert s.match('aba')
    assert s.match('abab')
    assert not s.match('abab', strict=True)
    assert not s.match('acb', strict=True)

    s = Sequence(Repeat(Or('a', 'b'), lb=1, ub=3, greedy=False))
    assert not s.match('')
    assert s.match('a')
    assert s.match('b')
    assert s.match('ba')
    assert s.match('aba')
    assert not s.match('aba', strict=True)

    s = Sequence(Repeat(Or('a', Sequence('b', 'c', 'd')), lb=1, ub=3))
    assert not s.match('')
    assert s.match('a')
    assert s.match('bcd')
    assert s.match('abcdbcd')
    assert s.match('abcda')
    assert s.match('aaa')
    assert s.match('bcdaa')
    assert not s.match('bcdaaa', strict=True)

    s = Sequence(Optional('a'))
    assert s.match('')
    assert s.match('a')
    assert not s.match('aa', strict=True)
    assert s.match('b')

    s = Sequence(ZeroOrMore('a'))
    assert s.match('')
    assert s.match('a')
    assert s.match('aaaaaaa')
    assert not s.match('aaab', strict=True)

    s = Sequence(int, float, Type(STR))
    assert s.match([1, 1.2, 'abc'])
    assert s.match([1, 1.2, u'abc'])

#-------------------------------------------------------------------------------
# Misc.

def test_misc():
    r = Repeat(1, lb=2, ub=1)
    assert_raises(ValueError, r.validate)

    t = Type(int)
    assert t.set == TypeWrapper(int)
    assert Type(TypeWrapper(int)).set == TypeWrapper(int)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
