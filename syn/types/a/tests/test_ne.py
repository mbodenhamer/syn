from nose.tools import assert_raises
from syn.types.a.ne import ValueExplorer, ExplorationError, DiffExplorer
from syn.base_utils import capture, assign

#-------------------------------------------------------------------------------
# NETypes

def test_netypes():
    from syn.types.a.ne import NEType, NotEqual, DiffersAtIndex, DiffersAtKey, \
        DifferentLength, DifferentTypes, SetDifferences, KeyDifferences

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

#-------------------------------------------------------------------------------
# ValueExplorer

def test_valueexplorer():
    x = ValueExplorer(1)

    assert x.value == 1
    assert x.current_value == 1
    assert x.display() == u'1'
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
    assert list(x.depth_first()) == []

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


    def last_line(si):
        return si.getvalue().split('\n')[-2]

    l = [1, [2, 3], [[4]]]
    r = ValueExplorer(l)
    with capture() as (out, err):
        r._eval('l')
        assert last_line(out) == '1'

        r._eval('n 2')
        r._eval('l')
        assert last_line(out) == '[[4]]'

        r._eval('d 2')
        r._eval('l')
        assert last_line(out) == '4'

        r._eval('u 2')
        r._eval('l')
        assert last_line(out) == '[[4]]'

        r._eval('n -1')
        r._eval('l')
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
        r._eval('l')
        assert last_lines(out) == ['A: 1', 'B: 1']

        r._eval('n 2')
        r._eval('l')
        assert last_lines(out) == ['A: [[4]]', 'B: [[5]]']

        r._eval('d 2')
        r._eval('l')
        assert last_lines(out) == ['A: 4', 'B: 5']

        r._eval('u 2')
        r._eval('l')
        assert last_lines(out) == ['A: [[4]]', 'B: [[5]]']

        r._eval('n -1')
        r._eval('l')
        assert last_lines(out) == ['A: [2, 3]', 'B: [2, 6]']

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

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
