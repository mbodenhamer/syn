import six
from nose.tools import assert_raises
from syn.base_utils import (GroupDict, AttrDict, assert_type_equivalent,
                            ReflexiveDict, SeqDict)
from syn.type.a import AnyType, TypeType
from syn.base.b.meta import Attr, Attrs, Meta, Data
from syn.base.a.meta import mro
from syn.base.b.base import create_hook

#-------------------------------------------------------------------------------
# Data Object

def test_data():
    d = Data()
    d.a = 1

    assert d.a == 1
    assert d.b == []

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
# Test _get_opt

@six.add_metaclass(Meta)
class GetOpt(object):
    _opts = dict(a = 1,
                 b = 2)
    _seq_opts = dict(a = [1, 2],
                     b = (3, 4))

def test_getopt():
    assert GetOpt._get_opt('a') == 1
    assert GetOpt._get_opt('b') == 2
    assert_raises(AttributeError, GetOpt._get_opt, 'c')
    assert GetOpt._get_opt('c', default=1) == 1
    assert GetOpt._get_opt('c', default=list) == []

#-------------------------------------------------------------------------------
# Test _populate_data

@six.add_metaclass(Meta)
class PopTest(object):
    _seq_opts = SeqDict(a = ('a1', 'a2'),
                        b = ['b1', 'b2'],
                        metaclass_lookup = ('a', 'b'))

    a1 = 1
    def a2(self):
        return self.a1 + 1

    @classmethod
    def b1(cls):
        return cls.a1 + 2

    @staticmethod
    def b2(x):
        return x + 3

class PopTest2(PopTest):
    @classmethod
    def b1(cls):
        return super(PopTest2, cls).b1() + 4

def test__populate_data():
    pt = PopTest()
    assert isinstance(PopTest._data.a, tuple)
    assert len(PopTest._data.a) == 2
    assert PopTest._data.a[0] == 1 == PopTest.a1

    a2 = PopTest._data.a[1]
    assert a2(pt) == 2

    assert isinstance(PopTest._data.b, list)
    assert len(PopTest._data.b) == 2
    b1 = PopTest._data.b[0]
    b2 = PopTest._data.b[1]

    assert b1() == 3
    assert b2(3) == 6

    
    pt = PopTest2()
    assert isinstance(PopTest2._data.a, tuple)
    assert len(PopTest2._data.a) == 2
    assert PopTest2._data.a[0] == 1 == PopTest2.a1

    a2 = PopTest2._data.a[1]
    assert a2(pt) == 2

    assert isinstance(PopTest2._data.b, list)
    assert len(PopTest2._data.b) == 2
    b1 = PopTest2._data.b[0]
    b2 = PopTest2._data.b[1]

    assert b1() == 7
    assert b2(3) == 6

#-------------------------------------------------------------------------------
# Test create hooks

@six.add_metaclass(Meta)
class CreateHooks(object):
    a = 1

    @classmethod
    @create_hook
    def hook1(cls):
        cls.a *= 2

class CHA(CreateHooks):
    _seq_opts = dict(create_hooks = ['hook2'],
                     metaclass_lookup = ['create_hooks'])
    a = 3

    @classmethod
    def hook2(cls):
        cls.b = 5

class PseudoHook(object):
    def __getattr__(self, attr):
        return type(self)

    def __call__(self):
        raise TypeError("Not Callable!!")

class CHBad(CreateHooks):
    a = 5
    b = PseudoHook()

def test_create_hooks():
    assert CreateHooks.a == 2
    assert CHA.a == 6
    assert CHA.b == 5

    ph = PseudoHook()
    assert_raises(TypeError, ph)
    assert ph.foobar is PseudoHook

    assert CHBad.a == 10
    assert isinstance(CHBad.b, PseudoHook)

#-------------------------------------------------------------------------------
# Test register_subclasses

@six.add_metaclass(Meta)
class Reg1(object):
    _opts = dict(register_subclasses = True)

class Reg2(Reg1):
    pass

class Reg3(Reg2):
    _opts = dict(register_subclasses = False)

@six.add_metaclass(Meta)
class Reg4(object):
    pass

class Reg5(Reg4):
    _opts = dict(register_subclasses = True)

class Reg6(object):
    pass

class Reg7(Reg5, Reg6):
    pass

def test_register_subclasses():
    assert Reg1._data.subclasses == [Reg1, Reg2]
    assert Reg2._data.subclasses == [Reg2]
    assert Reg3._data.subclasses == []

    assert Reg4._data.subclasses == []
    assert Reg5._data.subclasses == [Reg5, Reg7]
    assert not hasattr(Reg6, '_data')
    assert Reg7._data.subclasses == [Reg7]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
