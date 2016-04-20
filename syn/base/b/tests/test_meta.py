from syn.base_utils import GroupDict
from syn.type.a import AnyType, TypeType
from syn.base.b.meta import Attr, Attrs, Meta
from syn.base.a.tests.test_meta import test_meta as _test_meta

#-------------------------------------------------------------------------------
# Attr

def test_attr():
    a = Attr()
    assert isinstance(a.type, AnyType)
    assert a.default is None
    assert a.doc == ''
    assert a.optional is False
    assert a.call is None
    assert a.group is None
    assert a.groups is None

    a = Attr(int, 1, 'A number', optional=True, call=int, 
             group='c', groups=('a', 'b'))
    assert isinstance(a.type, TypeType)
    assert a.type.type is int
    assert a.default == 1
    assert a.doc == 'A number'
    assert a.optional is True
    assert a.call is int
    assert a.group == 'c'
    assert a.groups == ('a', 'b')

#-------------------------------------------------------------------------------
# Attrs

def test_attrs():
    attrs = Attrs(a = Attr(int, doc='value 1', group='a'),
                  b = Attr(float, 3.4, group='b'),
                  c = Attr(str, doc='value 2', optional=True, groups=['a', 'b']),
                  d = Attr(list, doc='value 3', optional=True, call=list)
                 )

    assert attrs.types['a'].type is int
    assert attrs.types['b'].type is float
    assert attrs.types['c'].type is str
    assert attrs.types['d'].type is list

    assert attrs.required == {'a', 'b'}
    assert attrs.optional == {'c', 'd'}
    assert attrs.defaults == dict(b = 3.4)
    assert attrs.doc == dict(a = 'value 1',
                             c = 'value 2',
                             d = 'value 3')

    assert attrs.call == dict(d = list)
    assert attrs.groups == GroupDict(a = set(['a', 'c']),
                                    b = set(['b', 'c']))

#-------------------------------------------------------------------------------
# Meta

def test_meta():
    _test_meta(Meta)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
