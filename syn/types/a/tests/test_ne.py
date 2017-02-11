from nose.tools import assert_raises
from syn.types.a import ValueExplorer, ExplorationError, DiffExplorer, visit
from syn.base_utils import capture, assign

#-------------------------------------------------------------------------------
# NETypes

def test_netypes():
    from syn.types.a import NEType, NotEqual, DiffersAtIndex, DiffersAtKey, \
        DifferentLength, DifferentTypes, SetDifferences, KeyDifferences, \
        DiffersAtAttribute

    class Foo(object):
        def __init__(self, a):
            self.a = a

    n = NEType(1, 2)
    assert str(n) == repr(n)
    x = n.explorer()
    assert x.current_value == (1, 2)
    
    assert n == NEType(1, 2)
    assert n != NEType(1, 3)
    assert n != NotEqual(1, 2)

    n = NotEqual(1, 2)
    assert str(n) == '1 != 2'
    
    accum = []
    def fake_explorer():
        def func():
            accum.append(1)
        return func

    assert sum(accum) == 0
    with capture() as (out, err):
        with assign(n, 'explorer', fake_explorer):
            n()
    assert sum(accum) == 1
    assert out.getvalue() == '1 != 2\n'

    l1 = [1, 2, 3]
    l2 = [1, 4, 3]
    n = DiffersAtIndex(l1, l2, 1)
    assert n.explorer().current_value == (2, 4)
    assert n.message() == 'Sequences differ at index 1: 2 != 4'

    assert DiffersAtIndex(l1, l2, 1) == DiffersAtIndex(l1, l2, 1)
    assert DiffersAtIndex(l1, l2, 1) != DiffersAtIndex(l1, l2, 2)
    assert DiffersAtIndex(l1, l2, 1) != DiffersAtIndex(l1, l1, 1)

    d1 = dict(a=1, b=2)
    d2 = dict(a=1, b=3)
    n = DiffersAtKey(d1, d2, key='b')
    assert n.explorer().current_value == (2, 3)
    assert n.message() == 'Mappings differ at key "b": 2 != 3'

    assert DiffersAtKey(d1, d2, 'a') == DiffersAtKey(d1, d2, 'a')
    assert DiffersAtKey(d1, d2, 'a') != DiffersAtKey(d1, d2, 'b')
    assert DiffersAtKey(d1, d2, 'a') != DiffersAtKey(d1, d1, 'a')

    l1 = [1, 2]
    l2 = [1, 2, 3]
    n = DifferentLength(l1, l2)
    assert n.message() == 'Different lengths: 2 != 3'

    l1 = [1, 2]
    l2 = (1, 2, 3)
    n = DifferentTypes(l1, l2)
    assert n.message() == ('Different types: {} != {}'
                           .format(str(list), str(tuple)))

    s1 = {1, 2, 3}
    s2 = {2, 3, 4}
    n = SetDifferences(s1, s2)
    assert n.message() == 'Exclusive items: {}'.format({1, 4})

    d1 = dict(a=1, b=2)
    d2 = dict(b=2)
    n = KeyDifferences(d1, d2)
    assert n.message() == 'Exclusive keys: {}'.format({'a'})
    n = KeyDifferences(d2, d1)
    assert n.message() == 'Exclusive keys: {}'.format({'a'})

    f1 = Foo(1)
    f2 = Foo(2)
    n = DiffersAtAttribute(f1, f2, 'a')
    assert n.message() == 'Objects differ at attribute "a": 1 != 2'
    assert n != NotEqual(1, 2)
    assert n.explorer().current_value == (1, 2)

#-------------------------------------------------------------------------------
# ValueExplorer

def test_valueexplorer():
    x = ValueExplorer(1)

    assert x.value == 1
    assert x.current_value == 1
    assert x.display() == u'1'
    with capture() as (out, err):
        x.command_display_value()
    assert out.getvalue() == '1\n'
    assert_raises(ExplorationError, x.step)
    assert_raises(ExplorationError, x.down)
    assert_raises(ExplorationError, x.up)

    x = ValueExplorer([1, 2, 3])
    assert x.current_value == 1
    x.step()
    assert x.current_value == 2
    x.step()
    assert x.current_value == 3
    assert_raises(ExplorationError, x.step)
    assert_raises(ExplorationError, x.up)
    x.down()
    assert x.value == 3
    assert x.current_value == 3
    x.up()
    assert x.value == [1, 2, 3]
    assert x.current_value == 3
    assert_raises(ExplorationError, x.step)
    x.down()
    assert x.value == 3
    x.up()
    assert x.current_value == 3
    x.step(-1)
    assert x.current_value == 2
    x.step()
    assert x.current_value == 1
    assert_raises(ExplorationError, x.step)
    x.step(1)
    assert x.current_value == 2
    x.step()
    assert x.current_value == 3
    assert_raises(ExplorationError, x.step)
    x.reset()
    assert list(x.depth_first()) == [[1, 2, 3], 1, 2, 3]

    x = ValueExplorer([])
    assert x.value == []
    assert x.current_value is None
    assert_raises(ExplorationError, x.step)
    assert list(x.depth_first()) == [[]]

    l = [1, [2, 3], 4]
    x = ValueExplorer(l)
    assert list(x.depth_first()) == [l, 1, [2, 3], 2, 3, 4]

    x = ValueExplorer(l, index=1)
    assert list(x.depth_first()) == [l, [2, 3], 2, 3, 4]

    x = ValueExplorer(l, index=2)
    assert list(x.depth_first()) == [l, 4]

    x = ValueExplorer(l, index=3)
    assert list(x.depth_first()) == []

    l = [1, [2, 3], [[4]]]
    x = ValueExplorer(l)
    assert list(x.depth_first()) == [l, 1, [2, 3], 2, 3, [[4]], [4], 4]

    d = dict(a=1, b=2)
    x = ValueExplorer(d)
    assert set(list(x.depth_first())[1:]) == {1, 2}

    d = dict(a=1, b=2, c=(3, 4))
    x = ValueExplorer(d)
    assert set(list(x.depth_first())[1:]) == {1, 2, (3, 4), 3, 4}

    assert ValueExplorer(d, key='a').current_value == 1
    assert ValueExplorer(d, key='b').current_value == 2
    assert ValueExplorer(d, key='c').current_value == (3, 4)
    assert_raises(ExplorationError, ValueExplorer, d, key='d')

    d = dict(a=1, b=2, c=dict(a=3, b=4))
    x = ValueExplorer(d)
    dfl = list(item for item in x.depth_first() if not isinstance(item, dict))
    assert set(dfl) == {1, 2, 3, 4}
    x.reset()
    assert set(x.depth_first(leaves_only=True)) == {1, 2, 3, 4}

    s = set()
    x = ValueExplorer(d, key='c')
    assert x.current_value == dict(a=3, b=4)
    x.down()
    s.add(x.current_value)
    x.step()
    s.add(x.current_value)
    assert_raises(ExplorationError, x.step)
    assert x.at_end
    assert s == {3, 4}

    s = 'abcd'
    x = ValueExplorer(s)
    assert list(x.depth_first()) == ['abcd', 'a', 'b', 'c', 'd']

    s = ''
    x = ValueExplorer(s)
    assert list(x.depth_first()) == ['']
    
    x = ValueExplorer([])
    assert list(x.depth_first()) == [[]]

    
    class Foo(object):
        def __init__(self, a, b):
            self.a = a
            self.b = b


    f = Foo(1, 2)
    x = ValueExplorer(f)
    assert list(x.depth_first()) == [f, 1, 2]
    #assert list(x.depth_first(leaves_only=True)) == [1, 2]

    x = ValueExplorer(f, attr='b')
    assert x.value is f
    assert x.current_value == 2
    assert x.attr == 'b'
    assert x.index == 1

    assert_raises(ExplorationError, ValueExplorer, f, attr='c')


    def last_line(si):
        return si.getvalue().split('\n')[-2]

    l = [1, [2, 3], [[4]]]
    r = ValueExplorer(l)
    with capture() as (out, err):
        r._eval('c')
        assert last_line(out) == '1'

        r._eval('l')
        assert last_line(out) == '[1, [2, 3], [[4]]]'

        r._eval('n 2')
        r._eval('c')
        assert last_line(out) == '[[4]]'

        r._eval('d 2')
        r._eval('c')
        assert last_line(out) == '4'

        r._eval('u 2')
        r._eval('c')
        assert last_line(out) == '[[4]]'

        r._eval('n -1')
        r._eval('c')
        assert last_line(out) == '[2, 3]'

#-------------------------------------------------------------------------------
# DiffExplorer

def test_diffexplorer():
    l1 = [1, 2, 3]
    l2 = [1, 2, 4]

    x = DiffExplorer(l1, l2)
    assert x.display() == u'A: 1\nB: 1'
    assert x.current_value == (1, 1)
    x.step()
    assert x.display() == u'A: 2\nB: 2'
    x.down()
    assert x.display() == u'A: 2\nB: 2'
    x.up()
    assert x.display() == u'A: 2\nB: 2'
    x.step()
    assert x.display() == u'A: 3\nB: 4'
    assert_raises(ExplorationError, x.step)
    x.step(-1)
    assert x.display() == u'A: 2\nB: 2'
    x.step()
    assert x.display() == u'A: 1\nB: 1'
    assert_raises(ExplorationError, x.step)
    
    x.reset()
    assert list(x.depth_first()) == [(l1, l2), (1, 1), (2, 2), (3, 4)]

    def last_lines(si):
        return si.getvalue().split('\n')[-3:-1]

    l1 = [1, [2, 3], [[4]]]
    l2 = [1, [2, 6], [[5]]]
    r = DiffExplorer(ValueExplorer(l1), ValueExplorer(l2))
    with capture() as (out, err):
        r._eval('c')
        assert last_lines(out) == ['A: 1', 'B: 1']

        r._eval('l')
        assert last_lines(out) == ['A: [1, [2, 3], [[4]]]',
                                   'B: [1, [2, 6], [[5]]]']

        r._eval('n 2')
        r._eval('c')
        assert last_lines(out) == ['A: [[4]]', 'B: [[5]]']

        r._eval('d 2')
        r._eval('c')
        assert last_lines(out) == ['A: 4', 'B: 5']

        r._eval('u 2')
        r._eval('c')
        assert last_lines(out) == ['A: [[4]]', 'B: [[5]]']

        r._eval('n -1')
        r._eval('c')
        assert last_lines(out) == ['A: [2, 3]', 'B: [2, 6]']

    d1 = dict(a = 1)
    d2 = dict(a = 2)
    r = DiffExplorer(d1, d2)
    with capture() as (out, err):
        r._eval('c')
        assert last_lines(out) == ['A: 1', 'B: 2']

        r._eval('l')
        assert last_lines(out) == ["A: {'a': 1}", "B: {'a': 2}"]

#-------------------------------------------------------------------------------
# Utilities

def test_deep_comp():
    from syn.types.a.ne import deep_comp
    from syn.base_utils import feq
    from functools import partial

    cfeq = partial(feq, tol=0.1)
    assert cfeq(4.05, 4.06)

    def comp(a, b, func=cfeq):
        if isinstance(a, float) and type(a) is type(b):
            return func(a, b)
        return a == b

    l1 = [1, 2, [3, 4.05]]
    l2 = [1, 2, [3, 4.06]]
    assert deep_comp(l1, l1)
    assert not deep_comp(l1, l2)
    assert not deep_comp(l1, l2, comp)
    assert deep_comp(l1, l2, comp, leaves_only=True)
    assert not deep_comp(l1, l2, partial(comp, func=partial(feq, tol=0.001)), 
                         leaves_only=True)

    dcomp = partial(deep_comp, func=comp, leaves_only=True)
    assert dcomp(l1, l2)

def test_deep_feq():
    from syn.types.a import deep_feq
    
    assert not deep_feq('abc', 'ab')
    assert deep_feq('abc', 'abc')
    assert deep_feq([], [])
    assert not deep_feq([], ())
    assert deep_feq([1, 2], [1, 2])
    assert not deep_feq([1, 2], [1])
    assert not deep_feq([[1, 2]], [(1, 2)])
    assert not deep_feq([[]], [()])
    
    assert not deep_feq(1, 1.01)
    assert not deep_feq(1j, 1.01j)
    assert deep_feq(1, 1.01, tol=0.1)
    assert deep_feq(1j, 1.01j, tol=0.1)
    
    assert not deep_feq([1], [1.01])
    assert deep_feq([1], [1.01], tol=0.1)
    assert deep_feq([1j], [1.01j], tol=0.1)

def test_is_visit_primitive():
    from syn.types.a import is_visit_primitive

    class Foo(object):
        pass
    
    f = Foo()

    assert is_visit_primitive(1)
    assert is_visit_primitive(int)
    assert is_visit_primitive(Foo)
    assert not is_visit_primitive([1, 2, 3])
    assert is_visit_primitive('a')
    assert not is_visit_primitive('ab')

    assert is_visit_primitive(f)
    assert list(visit(f)) == [f]

    f.a = 1
    assert not is_visit_primitive(f)
    assert list(visit(f)) == [('a', 1)]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
