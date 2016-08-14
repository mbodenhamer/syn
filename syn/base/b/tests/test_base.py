import six.moves.cPickle as pickle
from nose.tools import assert_raises
from syn.five import STR
from syn.base.b import Base, Attr, init_hook, coerce_hook, setstate_hook
from syn.type.a import Type
from syn.base_utils import assert_equivalent, assert_pickle_idempotent, \
    assert_inequivalent, assert_type_equivalent, \
    get_mod, SeqDict, is_hashable, this_module
from syn.base.b import check_idempotence

#-------------------------------------------------------------------------------
# Test basic functionality

class A(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(float),
                  c = Attr(STR, optional=True))
    _opts = dict(init_validate = True)

class A2(A):
    _opts = dict(id_equality = True)
    _attrs = dict(b = Attr(float, group=A.groups_enum().getstate_exclude))

class A3(A):
    _opts = dict(make_hashable = True)
    _attrs = dict(b = Attr(float, group=A.groups_enum().hash_exclude))

def test_base():
    kwargs = dict(a=5, b=3.4, c=u'abc')
    obj = A(**kwargs)

    assert obj.a == 5
    assert obj.b == 3.4
    assert obj.c == u'abc'
    
    assert obj.to_dict() == kwargs
    assert obj.to_tuple() == (5, 3.4, u'abc')
    assert obj.to_tuple(hash=True) == ('A', 5, 3.4, u'abc')
    assert not is_hashable(obj)

    assert obj != 5
    assert_equivalent(obj, A(**kwargs))
    assert_inequivalent(obj, A(a=6, b=3.4, c=u'abc'))

    assert A(a=5, b=3.4).to_dict() == dict(a=5, b=3.4)
    
    check_idempotence(obj)

    assert_raises(TypeError, A, a=5.1, b=3.4)
    assert_raises(AttributeError, A, a=5)

    assert_equivalent(A(**kwargs), A(**kwargs))
    assert_inequivalent(A2(**kwargs), A2(**kwargs))
    assert_raises(AssertionError, assert_pickle_idempotent, A2(**kwargs))

    obj2 = A2(**kwargs)
    assert_type_equivalent(obj2.to_dict(), dict(a=5, b=3.4, c=u'abc'))
    assert obj2.to_dict('getstate_exclude', include=True) == dict(b=3.4)

    obj3 = A3(**kwargs)
    assert obj3.to_tuple() == (5, 3.4, u'abc')
    assert obj3.to_tuple(hash=True) == ('A3', 5, u'abc')
    assert is_hashable(obj3)

#-------------------------------------------------------------------------------
# Test Positional Args

class B(A):
    _attrs = dict(b = Attr(float, default=1.2))
    _opts = dict(args = ('a', 'b'))

def test_positional_args():
    obj = B(5, 3.4, c=u'abc')

    assert obj.a == 5
    assert obj.b == 3.4
    assert obj.c == u'abc'

    assert B(5).to_dict() == dict(a=5, b=1.2)

    assert_raises(TypeError, B, 1, 2, 3)
    assert_raises(TypeError, B, 1, 2, a=1)

    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test arg coercion

class C(B):
    _opts = dict(coerce_args = True)

def test_arg_coercion():
    obj = C(5.1, 3)
    
    assert obj.a == 5
    assert obj.b == 3.0

    assert isinstance(obj.a, int)
    assert isinstance(obj.b, float)

    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test optional None

class D(C):
    _opts = dict(optional_none = True)

def test_optional_none():
    obj = D(5, 3.4)

    assert obj.a == 5
    assert obj.b == 3.4
    assert obj.c is None
    obj.validate()

    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test call


class E(B):
    _attrs = dict(d = Attr(list, None, call=list))

def test_call():
    obj = E(1, 2.1)
    
    assert obj.to_dict() == dict(a = 1,
                                 b = 2.1,
                                 d = [])

    assert E(1, 2.1, d=(1, 2)).to_dict() == dict(a = 1,
                                                 b = 2.1,
                                                 d = [1, 2])
    
    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test init

class F(B):
    _seq_opts = dict(init_order = ('d', 'e'))
    _attrs = dict(d = Attr(float, internal=True, 
                           init=lambda self: self.a + self.b),
                  e = Attr(float, internal=True,
                           init=lambda self: self.d + self.a))

class G(F):
    _attrs = dict(f = Attr(float, internal=True,
                           init=lambda self: 2.0 * self.a))

def test_init():
    obj = F(5, 3.4)
    assert obj.d == 8.4
    assert obj.e == 13.4

    check_idempotence(obj)

    obj = G(5, 3.4)
    assert obj.d == 8.4
    assert obj.e == 13.4
    assert obj.f == 10.0

    check_idempotence(obj)

    obj = F(5, 3.4, d=2.0)
    assert obj.d == 2.0
    assert obj.e == 7.0

    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test repr

class H(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(int, group='repr_exclude'))

def test_repr():
    obj = H(a = 1, b = 2)
    assert repr(obj) == "<{}.H {{'a': 1}}>".format(get_mod(H))

    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test coerce classmethod

class CT1(Base):
    _opts = dict(args = ('a',),
                 init_validate = True)
    _attrs = dict(a = Attr(int))

class CT2(Base):
    _opts = dict(init_validate = True,
                 coerce_args = True)
    _attrs = dict(a = Attr(int),
                  b = Attr(CT1))

class CT3(Base):
    _opts = dict(init_validate = True)
    _attrs = dict(a = Attr(int),
                  b = Attr(CT2),
                  c = Attr(CT1))

class CT4(Base):
    _attrs = dict(a = Attr(int))
    
    @classmethod
    def _coerce_hook(cls, value):
        value['a'] += 1
    _seq_opts = dict(coerce_hooks = ('_coerce_hook',))

class CT5(CT4):
    @classmethod
    def _coerce_hook(cls, value):
        super(CT5, cls)._coerce_hook(value)
        value['a'] += 2

class CT6(CT5):
    @classmethod
    @coerce_hook
    def _hook2(cls, value):
        value['a'] += 1

def test_coerce_classmethod():
    t1 = Type.dispatch(CT1)
    assert t1.coerce(1) == CT1(1)
    assert t1.coerce({'a': 1}) == CT1(1)
    assert t1.coerce({'a': 1.2}) == CT1(1)
    assert_raises(TypeError, t1.coerce, [1, 2])

    t2 = Type.dispatch(CT2)
    assert t2.coerce(dict(a=1, b=2)) == CT2(a=1, b=CT1(2))
    assert t2.coerce(dict(a=1, b=CT1(2))) == CT2(a=1, b=CT1(2))
    assert_raises(TypeError, t2.coerce, dict(a=1, b=2.3))
    assert t2.coerce(dict(a=1, b=dict(a=2.3))) == CT2(a=1, b=CT1(2))

    t3 = Type.dispatch(CT3)
    assert t3.coerce(dict(a=1, b=dict(a=2, b=3), c=4)) == \
        CT3(a=1, b=CT2(a=2, b=CT1(3)), c=CT1(4))
    assert t3.coerce(dict(a=1, b=dict(a=2, b=CT1(3)), c=4)) == \
        CT3(a=1, b=CT2(a=2, b=CT1(3)), c=CT1(4))
    assert_raises(TypeError, t3.coerce, dict(a=1, b=dict(a=2, b=3.1), c=4))
    assert t3.coerce(dict(a=1, b=dict(a=2, b=dict(a=3.1)), c=4)) == \
        CT3(a=1, b=CT2(a=2, b=CT1(3)), c=CT1(4))

    obj = t3.coerce(dict(a=1, b=dict(a=2, b=3), c=4))
    check_idempotence(obj)

    t4 = Type.dispatch(CT4)
    assert t4.coerce(dict(a = 1)) == CT4(a = 2)

    t5 = Type.dispatch(CT5)
    assert t5.coerce(dict(a = 1)) == CT5(a = 4)

    t6 = Type.dispatch(CT6)
    assert t6.coerce(dict(a = 1)) == CT6(a = 5)

#-------------------------------------------------------------------------------
# Init & setstate hooks

class I(B):
    _seq_opts = SeqDict()
    _attrs = dict(d = Attr(float, internal=True),
                  e = Attr(float, internal=True))
    
    def _foo(self):
        self.d = self.a * self.b

    def _bar(self):
        self.e = self.d + 2

    _seq_opts.init_hooks = ('_foo', '_bar')

class I2(I):
    _attrs = dict(f = Attr(float, internal=True))

    @init_hook
    def _baz(self):
        self.f = self.d + self.e

class I2a(I2):
    pass

class I2b(I2):
    def _baz(self):
        self.f = super(I2a, self)._baz() + 1 # pragma: no cover

class I3(I2):
    @setstate_hook
    def _foobaz(self):
        self.f += 1

class I4(I):
    _attrs = dict(f = Attr(int))

    @init_hook
    @setstate_hook
    def _baz(self):
        if not hasattr(self, 'f'):
            self.f = self.a
        else:
            self.f += 1

def test_init_setstate_hooks():
    obj = I(5, 2.5)
    assert obj.d == 12.5
    assert obj.e == 14.5

    check_idempotence(obj)

    obj = I2(5, 2.5)
    assert obj.d == 12.5
    assert obj.e == 14.5
    assert obj.f == 27.0

    check_idempotence(obj)

    # Inheriting without overriding preserves the init hook
    obj = I2a(5, 2.5)
    assert obj.d == 12.5
    assert obj.e == 14.5
    assert obj.f == 27.0

    check_idempotence(obj)

    # Because we overrode _baz without specifying init_hook again
    assert_raises(AttributeError, I2b, 5, 2.5)

    obj = I3(5, 2.5)
    assert obj.f == 27.0
    obj2 = pickle.loads(pickle.dumps(obj))
    assert obj2.f == 28.0

    obj = I4(5, 2.5)
    assert obj.f == 5
    obj2 = pickle.loads(pickle.dumps(obj))
    assert obj2.f == 6

    assert_raises(TypeError, I, 5.2, 2) # Sanity check for init_validate

#-------------------------------------------------------------------------------
# Conversion classmethods

class ConvTest(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(float),
                  c = Attr(STR))
    _opts = dict(args = ('a', 'b', 'c'),
                 init_validate = True)

def test_mapping_conversion():
    dct = dict(a = 1, b = 2.3, c = 'abc')
    assert_equivalent(Base._dict_from_mapping(dct), dct)

    ct1 = ConvTest(1, 2.3, 'abc')
    assert_equivalent(ConvTest.from_mapping(dct), ct1)

def test_object_conversion():
    class Foo(object): pass
    obj = Foo()
    obj.a = 1
    obj.b = 2.3
    obj.c = 'abc'
    obj.d = 'def'
    
    ct1 = ConvTest(1, 2.3, 'abc')
    ct2 = ConvTest.from_object(obj)
    assert_equivalent(ct2, ct1)
    assert not hasattr(ct2, 'd')

def test_sequence_conversion():
    seq = [1, 2.3, 'abc']
    seq2 = seq + ['def']
    assert ConvTest._dict_from_sequence(seq) == dict(a = 1, b = 2.3, c = 'abc')

    ct1 = ConvTest(1, 2.3, 'abc')
    assert_equivalent(ConvTest.from_sequence(seq), ct1)
    assert_raises(ValueError, ConvTest.from_sequence, seq2)

#-------------------------------------------------------------------------------
# getstate_exclude

class GSEx(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(int, groups = ('getstate_exclude',),
                           init = lambda self: self.a + 1))
    _opts = dict(init_validate = True,
                 args = ('a',))

class GSEx2(GSEx):
    @init_hook
    @setstate_hook
    def _set_b(self):
        self.b = self.a + 1

def test_getstate_exclude():
    obj = GSEx(1)
    assert obj.a == 1
    assert obj.b == 2
    assert_raises(AssertionError, check_idempotence, obj)

    obj = GSEx2(1)
    assert obj.a == 1
    assert obj.b == 2
    check_idempotence(obj)

#-------------------------------------------------------------------------------
# Test str

class StrTest(Base):
    _attrs = dict(a = Attr(list),
                  b = Attr(float, groups=('str_exclude', 'eq_exclude')),
                  c = Attr(str))

def test_base_str():
    obj = StrTest(a = [1, 2], b = 1.2, c = 'abc')
    assert str(obj) == "StrTest(a = [1, 2], c = 'abc')"

    pretty_str = '''StrTest(a = [1,
             2],
        c = 'abc')'''
    assert obj.pretty() == pretty_str
    assert_equivalent(eval(obj.pretty()), obj)

#-------------------------------------------------------------------------------
# Test attr_documentation_order

class ADO(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(int),
                  c = Attr(int))

class ADO2(ADO):
    _opts = dict(args = ('b',))

def test_attr_documentation_order():
    assert ADO._data.attr_documentation_order == ['a', 'b', 'c']
    assert ADO2._data.attr_documentation_order == ['b', 'a', 'c']

    assert ADO._data.kw_attrs == ['a', 'b', 'c']
    assert ADO2._data.kw_attrs == ['a', 'c']

#-------------------------------------------------------------------------------
# Test class auto-documentation


class ADOC(Base):
    '''Some documentation.'''
    _attrs = dict(a = Attr(int, doc='attr a'),
                  b = Attr(float, optional=True),
                  c = Attr(int, 2, optional=True, doc='attr c'))
    _opts = dict(args = ('a', 'b', 'c'))
    
    def __init__(self, *args, **kwargs):
        '''Some more documentation.'''
        super(ADOC, self).__init__(*args, **kwargs)

class ADOC2(Base):
    _opts = dict(autodoc = False)

def test_class_auto_documentation():
    assert ADOC._generate_documentation_signature(ADOC._opts.args) == \
        'ADOC(a, [b], [c=2], **kwargs)'

    assert ADOC._generate_documentation_attrspec(ADOC._opts.args) == \
        ('a: *int*\n'
         '    attr a\n'
         'b [**Optional**]: *float*\n'
         'c [**Optional**] (*default* = 2): *int*\n'
         '    attr c')

    ADOC(1, 1.2)

#-------------------------------------------------------------------------------
# Repr template

class REPR1(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(float))
    _opts = dict(repr_template = '<{__mod__}.{__name__} a={a} b={b}>',
                 init_validate = True)

def test_repr_template():
    r = REPR1(a = 1, b = 2.3)
    assert repr(r) == '<{}.REPR1 a=1 b=2.3>'.format(this_module().__name__)

    r._opts.repr_template = '{b}'
    assert repr(r) == '2.3'

#-------------------------------------------------------------------------------
# Test generation

class Gen1(Base):
    _attrs = dict(a = Attr(int),
                  b = Attr(float),
                  c = Attr(str, optional=True, group='generate_exclude'))

def test_generation():
    g = Gen1._generate()
    g.validate()

    assert isinstance(g.a, int)
    assert isinstance(g.b, float)
    assert not hasattr(g, 'c')

#-------------------------------------------------------------------------------
# Update functionality

class TestUpdate(Base):
    pass

def test_update():
    pass

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
