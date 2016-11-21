from nose.tools import assert_raises
from syn.types.a.ne import Value, FindNE, ValueExplorer, ExplorationError, \
    DiffExplorer

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

#-------------------------------------------------------------------------------
# DiffExplorer


def test_diffexplorer():
    l1 = [1, 2, 3]
    l2 = [1, 2, 4]

    x = DiffExplorer(l1, l2)
    assert x.display() == u'A: 1\nB: 1'
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

#-------------------------------------------------------------------------------
# Value

def test_value():
    v = Value(1)
    assert v() == 1
    assert v != 1

    assert v == Value(1)
    assert v != Value(2)

#-------------------------------------------------------------------------------
# FindNe

def test_findNe():
    FindNE

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
