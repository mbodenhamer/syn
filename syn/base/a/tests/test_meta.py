import six
from syn.five import STR, xrange
from syn.type.a import AnyType, TypeType
from syn.base.a.meta import combine, graft, AttrDict, sorted_bases, \
    metaclasses, mro, Attr, Attrs, Meta

#-------------------------------------------------------------------------------
# Utilities

def test_combine():
    d1 = AttrDict(a = 1, b = 2)
    d2 = dict(b = 3, c = 4)

    d3 = combine(d1, d2)
    assert type(d3) is AttrDict
    assert d3['a'] == 1
    assert d3['b'] == 3
    assert d3['c'] == 4

    d4 = combine(d2, d1)
    assert type(d4) is dict
    assert d4['a'] == 1
    assert d4['b'] == 2
    assert d4['c'] == 4

def test_graft():
    lst = list(xrange(0,5))
    branch = [6,7,8]
    
    g1 = graft(lst, branch, 2)
    assert g1 == [0, 1, 6, 7, 8, 2, 3, 4]

    g2 = graft(lst, branch, 5)
    assert g2 == [0, 1, 2, 3, 4, 6, 7, 8]

    g3 = graft(lst, branch, 0)
    assert g3 == [6,7,8, 0,1,2,3,4]

def test_metaclasses():
    class M1(type): pass
    class M2(M1): pass
    class M3(type): pass

    class A(object): pass
    @six.add_metaclass(M1)
    class B(object): pass
    @six.add_metaclass(M3)
    class C(object): pass
    @six.add_metaclass(M2)
    class D(object): pass
    class E(D): pass

    assert metaclasses([A]) == []
    assert metaclasses([B]) == [M1]
    assert metaclasses([C]) == [M3]
    assert metaclasses([C, B, A]) == [M3, M1]
    assert metaclasses([D, C, B, A]) == [M2, M3, M1]
    assert metaclasses([D, C]) == [M2, M3]
    assert metaclasses([E, C]) == [M2, M3]

    # sanity check for six.add_metaclass
    assert mro(A) == [A, object]
    assert mro(B) == [B, object]
    assert mro(C) == [C, object]
    assert mro(D) == [D, object]

def test_sorted_bases():
    class A(object): pass
    class B(A): pass
    class C(B): pass
    class D(C): pass

    class X(object): pass
    class Y(X): pass
    class Z(Y): pass

    class E(D, Z): pass
    class F(D): pass
    class G(D): pass
    class H(G, F): pass
    class I(H, E): pass
    class J(E, H): pass

    l1 = sorted_bases([D])
    l2 = sorted_bases([C])
    l3 = sorted_bases([E])
    l3_2 = sorted_bases([D,Z])
    l4 = sorted_bases([H])
    l4_2 = sorted_bases([G,F])
    l5 = sorted_bases([I])
    l5_2 = sorted_bases([H,E])
    l6 = sorted_bases([J])
    l6_2 = sorted_bases([E,H])

    assert l1 == [D, C, B, A]
    assert l2 == [C, B, A]
    assert l3 == [E, D, C, B, A, Z, Y, X]
    assert l3_2 == l3[1:]
    assert l4 == [H, G, F, D, C, B, A]
    assert l4_2 == l4[1:]
    assert l5 == [I, H, G, F, E, D, C, B, A, Z, Y, X]
    assert l5_2 == l5[1:]
    assert l6 == [J, E, H, G, F, D, C, B, A, Z, Y, X]
    assert l6_2 == l6[1:]

    assert sorted_bases([type]) == []
    
#-------------------------------------------------------------------------------
# Object Attribute

def test_attr():
    a = Attr()
    assert isinstance(a.type, AnyType)
    assert a.default is None
    assert a.doc == ''
    assert a.optional is False

    a = Attr(int, 1, 'A number', optional=True)
    assert isinstance(a.type, TypeType)
    assert a.type.type is int
    assert a.default == 1
    assert a.doc == 'A number'
    assert a.optional is True

#-------------------------------------------------------------------------------
# Object Attrs Bookkeeping

def test_attrs():
    attrs = Attrs(a = Attr(int, doc='value 1'),
                  b = Attr(float, 3.4),
                  c = Attr(STR, doc='value 2', optional=True),
                  d = Attr(list, [1, 2], doc='value 3', optional=True)
                 )

    assert attrs.attrs == set(['a', 'b', 'c', 'd'])
    assert attrs.types['a'].type is int
    assert attrs.types['b'].type is float
    assert attrs.types['c'].type is STR[0]
    assert attrs.types['d'].type is list

    assert attrs.required == {'a', 'b'}
    assert attrs.optional == {'c', 'd'}
    assert attrs.defaults == dict(b = 3.4,
                                  d = [1, 2])
    assert attrs.doc == dict(a = 'value 1',
                             c = 'value 2',
                             d = 'value 3')

#-------------------------------------------------------------------------------
# Metaclass

def test_meta():
    @six.add_metaclass(Meta)
    class A(object):
        _attrs = Attrs(a = Attr(int, doc='value 1'),
                       b = Attr(float, 3.4),
                       c = Attr(STR, doc='value 2', optional=True)
                      )
        _opts = AttrDict(x = 1,
                         y = 2.3)

    class B(A):
        _attrs = dict(c = Attr(dict),
                      d = Attr(list, default=[1, 2]))
        _opts = dict(y = 3.4,
                     z = 'abc')

    assert A._attrs.types['a'].type is int
    assert A._attrs.types['b'].type is float
    assert A._attrs.types['c'].type is STR[0]

    assert A._attrs.required == {'a', 'b'}
    assert A._attrs.optional == {'c'}
    assert A._attrs.defaults == dict(b = 3.4)
    assert A._attrs.doc == dict(a = 'value 1',
                                c = 'value 2')
    assert A._attrs.attrs == set(['a', 'b', 'c'])

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


    assert A._opts == dict(x = 1, y = 2.3)
    assert B._opts == dict(x = 1, y = 3.4, z = 'abc')


    class M1(type):
        pass

    @six.add_metaclass(M1)
    class C(object):
        _attrs = Attrs(a = Attr(float),
                       e = Attr(set))

    class M2(Meta, M1): pass
    class D(six.with_metaclass(M2, B, C)):
        pass

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

    assert D._opts == dict(x = 1, y = 3.4, z = 'abc')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
