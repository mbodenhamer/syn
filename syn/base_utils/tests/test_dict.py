from nose.tools import assert_raises
from syn.base_utils import (AttrDict, UpdateDict, GroupDict, ReflexiveDict,
                            SeqDict, AssocDict)
from syn.base_utils.dict import dict_arg, is_assoc_list

#-------------------------------------------------------------------------------
# Utilities

def test_is_assoc_list():
    assert not is_assoc_list((1, 2))
    assert not is_assoc_list([1, 2])
    assert not is_assoc_list([(1, 2, 3)])
    assert is_assoc_list([(1, 2), (3, 4)])

def test_dict_arg():
    assert dict_arg() == {}
    assert dict_arg(dict(a = 1, b = 2)) == dict(a = 1, b = 2)
    assert dict_arg(a = 1, b = 2) == dict(a = 1, b = 2)
    assert dict_arg([('a', 1), ('b', 2)]) == [('a', 1), ('b', 2)]
    assert_raises(TypeError, dict_arg, 1)
    assert_raises(TypeError, dict_arg, 1, 2)

#-------------------------------------------------------------------------------
# AttrDict

def test_attrdict():
    obj = AttrDict(a = 1, b = 2)
    print(obj)

    assert obj['a'] == 1
    assert obj.a == 1
    assert obj['b'] == 2
    assert obj.b == 2

    del obj.b
    assert 'b' not in obj
    
    def test_get_item(key):
        return obj[key]
    def test_del_item(key):
        del obj[key]

    assert_raises(KeyError, test_get_item, 'b')
    assert_raises(AttributeError, getattr, obj, 'b')
    assert_raises(KeyError, test_del_item, 'b')
    assert_raises(AttributeError, delattr, obj, 'b')

    obj.a = 3
    assert obj['a'] == 3

    obj.c = 5
    assert obj['c'] == 5
    assert obj.c == 5

#-------------------------------------------------------------------------------
# UpdateDict

def test_updatedict():
    assert_raises(NotImplementedError, UpdateDict)

    class Dict(UpdateDict):
        def _update(self):
            self.count = len(self)

    d = Dict(a = 1, b = 2)
    assert d == dict(a = 1, b = 2)
    assert d.count == 2
    
    d['a'] = 3
    assert d == dict(a = 3, b = 2)
    assert d.count == 2

    d['c'] = 4
    assert d == dict(a = 3, b = 2, c = 4)
    assert d.count == 3
    
    del d['c']
    assert d == dict(a = 3, b = 2)
    assert d.count == 2

    d.update(dict(a = 1, c = 3))
    assert d == dict(a = 1, b = 2, c = 3)
    assert d.count == 3

#-------------------------------------------------------------------------------
# GroupDict

def test_groupdict():
    dct = GroupDict(a = set([1, 2, 3]),
                    b = set([3, 4, 5]))

    assert dct.union() == set([1, 2, 3, 4, 5])
    assert dct.intersection() == set([3])
    assert dct.complement('a') == set([4, 5])
    assert dct.complement('b') == set([1, 2])

    dct2 = GroupDict(b = set([5, 6]),
                     c = set([6, 7]))
    dct.update(dct2)
    assert dct == dict(a = set([1, 2, 3]),
                       b = set([3, 4, 5, 6]),
                       c = set([6, 7]))

    assert dct.union() == set(range(1, 8))
    assert dct.union('a', 'c') == set([1, 2, 3, 6, 7])

    assert dct.intersection() == set()
    assert dct.intersection('a', 'b') == set([3])

    assert dct.complement('a') == set(range(4, 8))
    assert dct.complement('a', 'b') == set([7])

#-------------------------------------------------------------------------------
# ReflexiveDict

def test_reflexivedict():
    dct = ReflexiveDict('a', 'b', 'c')
    assert dct == dict(a = 'a',
                       b = 'b',
                       c = 'c')

    dct.d = 1
    assert dct.d == 'd'

#-------------------------------------------------------------------------------
# SeqDict

def test_seqdict():
    dct = SeqDict(a = [1, 2],
                  b = (10, 11))

    assert dct.a == [1, 2]
    assert dct.b == (10, 11)

    dct.update(dict(a = (3, 4),
                    b = [12, 13],
                    c = [20]))
    assert dct.a == [1, 2, 3, 4]
    assert dct.b == (10, 11, 12, 13)
    assert dct.c == [20]

#-------------------------------------------------------------------------------
# AssocDict

def test_assocdict():
    dct = AssocDict(a = 1, b = 1.2)
    assert dct == dict(a = 1, b = 1.2)

    dct = AssocDict([('a', 1), ('b', 2), ('c', 3)])
    assert list(dct) == ['a', 'b', 'c']
    assert len(dct) == 3
    dct.update([('d', 4), ('c', 5), ('e', 6)])
    assert list(dct) == ['a', 'b', 'c', 'd', 'e']
    assert dct == dict(a = 1, b = 2, c = 5, d = 4, e = 6)
    del dct['b']
    assert list(dct) == ['a', 'c', 'd', 'e']
    assert dct == dict(a = 1, c = 5, d = 4, e = 6)
    assert 'b' not in dct
    
    dct = AssocDict(a = 1)
    assert repr(dct) == "{'a': 1}"

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
