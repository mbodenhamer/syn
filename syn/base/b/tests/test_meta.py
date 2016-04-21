import six
from syn.base_utils import (GroupDict, AttrDict, assert_type_equivalent,
                            ReflexiveDict)
from syn.type.a import AnyType, TypeType
from syn.base.b.meta import Attr, Attrs, Meta
from syn.base.a.meta import mro

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
    fe = lambda self: self.a + 1
    attrs = Attrs(a = Attr(int, doc='value 1', group='a'),
                  b = Attr(float, 3.4, group='b'),
                  c = Attr(str, doc='value 2', optional=True, groups=['a', 'b']),
                  d = Attr(list, doc='value 3', optional=True, call=list),
                  e = Attr(int, internal=True, init=fe),
                 )

    assert attrs.attrs == set(['a', 'b', 'c', 'd', 'e'])
    assert attrs.types['a'].type is int
    assert attrs.types['b'].type is float
    assert attrs.types['c'].type is str
    assert attrs.types['d'].type is list
    assert attrs.types['e'].type is int

    assert attrs.required == {'a', 'b', 'e'}
    assert attrs.optional == {'c', 'd'}
    assert attrs.defaults == dict(b = 3.4)
    assert attrs.doc == dict(a = 'value 1',
                             c = 'value 2',
                             d = 'value 3')

    assert attrs.call == dict(d = list)
    assert attrs.init == dict(e = fe)
    assert attrs.internal == set(['e'])
    assert attrs.groups == GroupDict(a = set(['a', 'c']),
                                     b = set(['b', 'c']))

#-------------------------------------------------------------------------------
# Meta

def test_meta():
    @six.add_metaclass(Meta)
    class A(object):
        _groups = ReflexiveDict('g1', 'g2')
        _attrs = Attrs(a = Attr(int, doc='value 1', group=_groups.g1),
                       b = Attr(float, 3.4, group=_groups.g2),
                       c = Attr(str, doc='value 2', optional=True)
                      )
        _opts = AttrDict(x = 1,
                         y = 2.3)

    class B(A):
        _attrs = dict(c = Attr(dict, group=A.groups_enum().g1),
                      d = Attr(list, default=[1, 2]))
        _opts = dict(y = 3.4,
                     z = 'abc')

    assert A._attrs.types['a'].type is int
    assert A._attrs.types['b'].type is float
    assert A._attrs.types['c'].type is str

    assert A._attrs.required == {'a', 'b'}
    assert A._attrs.optional == {'c'}
    assert A._attrs.defaults == dict(b = 3.4)
    assert A._attrs.doc == dict(a = 'value 1',
                                c = 'value 2')
    assert A._attrs.attrs == set(['a', 'b', 'c'])
    assert_type_equivalent(A._groups,
                           GroupDict(_all = set(['a', 'b', 'c']),
                                     _internal = set([]),
                                     g1 = set(['a']),
                                     g2 = set(['b'])))

    assert B._attrs.types['a'].type is int
    assert B._attrs.types['b'].type is float
    assert B._attrs.types['c'].type is dict
    assert B._attrs.types['d'].type is list

    assert B._attrs.required == {'a', 'b', 'c', 'd'}
    assert B._attrs.optional == set([])
    assert B._attrs.defaults == dict(b = 3.4,
                                     d = [1, 2])
    assert B._attrs.doc == dict(a = 'value 1')
    assert B._attrs.attrs == set(['a', 'b', 'c', 'd'])
    assert_type_equivalent(B._groups,
                           GroupDict(_all = set(['a', 'b', 'c', 'd']),
                                     _internal = set([]),
                                     g1 = set(['a', 'c']),
                                     g2 = set(['b'])))


    assert A._opts == dict(x = 1, y = 2.3)
    assert B._opts == dict(x = 1, y = 3.4, z = 'abc')


    class M1(type):
        pass

    @six.add_metaclass(M1)
    class C(object):
        _attrs = Attrs(a = Attr(float),
                       e = Attr(set, internal=True))

    class M2(Meta, M1): pass
    class D(six.with_metaclass(M2, B, C)):
        _groups = ReflexiveDict('g3')

    assert mro(D) == [D, B, A, C, object]

    assert D._attrs.types['a'].type is int
    assert D._attrs.types['b'].type is float
    assert D._attrs.types['c'].type is dict
    assert D._attrs.types['d'].type is list
    assert D._attrs.types['e'].type is set

    assert D._attrs.required == {'a', 'b', 'c', 'd', 'e'}
    assert D._attrs.optional == set([])
    assert D._attrs.defaults == dict(b = 3.4,
                                     d = [1, 2])
    assert D._attrs.doc == dict(a = 'value 1')

    assert_type_equivalent(D._groups,
                           GroupDict(_all = set(['a', 'b', 'c', 'd', 'e']),
                                     _internal = set(['e']),
                                     g1 = set(['a', 'c']),
                                     g2 = set(['b']),
                                     g3 = set()))

    assert_type_equivalent(D._opts, AttrDict(x = 1, y = 3.4, z = 'abc'))

    # Test default blank attrs
    @six.add_metaclass(Meta)
    class E(object):
        pass

    assert_type_equivalent(E._opts, AttrDict())
    assert_type_equivalent(E._attrs, Attrs())
    assert_type_equivalent(E._groups, GroupDict())

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
