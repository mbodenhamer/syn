import collections
from copy import deepcopy
from nose.tools import assert_raises
from syn.base.b import ListWrapper, Attr
from syn.base.b.tests.test_base import check_idempotence

#-------------------------------------------------------------------------------
# ListWrapper

def test_listwrapper():
    obj = ListWrapper(1, 2, 3)
    check_idempotence(obj)

    assert isinstance(obj, collections.MutableSequence)
    assert issubclass(ListWrapper, collections.MutableSequence)

    cobj = deepcopy(obj)
    _list = list(range(10))
    cobj._list = list(_list)

    assert list(cobj) == _list
    cobj.append(11)
    assert list(cobj) == _list + [11]
    cobj.extend([12,13])
    assert list(cobj) == _list + [11, 12, 13]
    cobj.insert(0, 14)
    assert list(cobj) == [14] + _list + [11, 12, 13]
    cobj.pop()
    assert list(cobj) == [14] + _list + [11, 12]
    cobj.remove(12)
    assert list(cobj) == [14] + _list + [11]

    assert cobj.count(1) == 1
    assert cobj.index(0) == 1

    cobj.sort()
    assert list(cobj) == _list + [11, 14]

    assert cobj[-1] == 14
    cobj[-1] = 15
    assert list(cobj) == _list + [11, 15]
    del cobj[-1]

    cobj.reverse()
    _list.reverse()
    assert list(cobj) == [11] + _list
    
    class LW1(ListWrapper):
        _opts = dict(max_len = 1,
                     min_len = None)

    class LW2(ListWrapper):
        _opts = dict(max_len = None,
                     min_len = 50)

    assert_raises(ValueError, LW1(_list=_list).validate)
    assert_raises(ValueError, LW2(_list=_list).validate)

    class LW3(ListWrapper):
        _attrs = dict(a = Attr(int),
                      b = Attr(float))

    lw = LW3(1, 2, 3, a = 1, b = 1.2)
    assert str(lw) == "LW3(1, 2, 3, a = 1, b = 1.2)"
    pretty_lw = '''LW3(1,
    2,
    3,
    a = 1,
    b = 1.2)'''
    assert lw.pretty() == pretty_lw

#-------------------------------------------------------------------------------
# Test ListWrapper Positional Args

class LWPA(ListWrapper):
    _opts = dict(max_len = 3,
                 args = ['a', 'b'],
                 init_validate = True)
    _attrs = dict(a = Attr(int),
                  b = Attr(float, default=3.2))

def test_listwrapper_positional_args():
    lw = LWPA(1, 1.2, 'abc', 4)
    assert list(lw) == [1, 1.2, 'abc']
    assert lw.a == 4
    assert lw.b == 3.2
    check_idempotence(lw)

    lw = LWPA(1, 1.2, 'abc', 4, 5.3)
    assert list(lw) == [1, 1.2, 'abc']
    assert lw.a == 4
    assert lw.b == 5.3
    check_idempotence(lw)

    assert_raises(TypeError, LWPA, 1, 1.2, 'abc', 4, 5.3, 6.5)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
