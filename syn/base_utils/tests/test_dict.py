# pylint: disable=W0212

from nose.tools import assert_raises
from syn.base_utils import AttrDict, UpdateDict

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

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
