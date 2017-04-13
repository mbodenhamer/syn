import collections
from copy import deepcopy
from nose.tools import assert_raises
from syn.base.b import ListWrapper, Attr
from syn.base.b.tests.test_base import check_idempotence
from syn.types.a import generate
from syn.type.a import Schema
from syn.schema.b.sequence import Sequence
from syn.base_utils import assert_equivalent

#-------------------------------------------------------------------------------
# ListWrapper

def test_listwrapper():
    obj = ListWrapper(1, 2, 3)
    check_idempotence(obj)

    objc = obj.copy()
    assert_equivalent(obj, objc)
    assert_equivalent(obj._list, objc._list)
    assert obj._list is not objc._list

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
# Test ListWrapper Generation

class LWGT1(ListWrapper):
    _opts = dict(init_validate = True)
    _attrs = dict(a = Attr(int))

class LWGT2(LWGT1):
    _opts = dict(min_len = 2)

class LWGT3(LWGT1):
    _attrs = dict(_list = Attr(Schema(Sequence(int, float, int))))

class LWGT4(LWGT2):
    _opts = dict(max_len = 4)

def test_listwrapper_generation():
    lw1 = generate(LWGT1)
    assert isinstance(lw1.a, int)
    assert len(lw1) == 0
    
    lw2 = generate(LWGT2)
    assert isinstance(lw2.a, int)
    assert len(lw2) == 2

    lw3 = generate(LWGT3)
    assert isinstance(lw2.a, int)
    assert len(lw3) == 3
    assert isinstance(lw3[0], int)
    assert isinstance(lw3[1], float)
    assert isinstance(lw3[2], int)

    lw4 = generate(LWGT4)
    assert 2 <= len(lw4) <= 4

    lw41 = generate(LWGT4, max_len=3)
    assert 2 <= len(lw41) <= 3

    assert_raises(TypeError, LWGT1, [], a=1.2)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
