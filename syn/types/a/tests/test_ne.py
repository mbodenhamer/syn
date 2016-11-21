from nose.tools import assert_raises
from syn.types.a.ne import Value, FindNE, ValueExplorer, ExplorationError

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

    # x = ValueExplorer([])

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
