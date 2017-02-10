import six
import sys
from nose.tools import assert_raises
from syn.base_utils import hasmethod, mro, import_module, message, assign, \
    capture

#-------------------------------------------------------------------------------
# Printing utilities

def test_eprint():
    from syn.base_utils import eprint, capture

    with capture() as (out, err):
        eprint('abc')

    assert out.getvalue() == ''
    assert err.getvalue() == 'abc\n'

#-------------------------------------------------------------------------------
# Class utilities

def test_subclasses():
    from syn.base_utils import subclasses

    class A(object): pass
    class B(A): pass
    class C(A): pass
    class D(B): pass
    class E(B): pass
    class F(D): pass
    class G(C): pass

    assert subclasses(A) == [B, D, F, E, C, G]
    assert subclasses(G) == []
    assert subclasses(C) == [G]

def test_mro():
    import abc

    assert mro(type) == [type]
    assert mro(int) == [int, object]
    assert mro(1) == [int, object]
    assert mro(abc.ABCMeta) == [abc.ABCMeta]

def test_is_subclass():
    from syn.base_utils import is_subclass

    class Foo(object):
        pass

    class Bar(Foo):
        pass

    assert is_subclass(Bar, Foo)
    assert not is_subclass(Foo, Bar)
    assert not is_subclass(Foo(), Bar)
    assert_raises(TypeError, is_subclass, Foo, Bar())

class Methods(object):
    a = 1

    def bar(self):
        pass

    @classmethod
    def cbar(cls):
        pass

    @staticmethod
    def sbar():
        pass


def test_hasmethod():
    Foo = Methods

    f = Foo()
    f.bar()
    Foo.cbar()
    Foo.sbar()

    assert hasmethod(f, 'bar')
    assert hasmethod(Foo, 'bar')

    assert not hasmethod(f, 'a')
    assert not hasmethod(f, 'foo')

    assert hasmethod(f, 'cbar')
    assert hasmethod(Foo, 'cbar')

    assert not hasmethod(f, 'sbar')
    if six.PY2:
        assert not hasmethod(Foo, 'sbar')
    else:
        assert hasmethod(Foo, 'sbar')

def test_callables():
    from syn.base_utils import callables
    Foo = Methods

    f = Foo()
    f.b = 2
    f.c = lambda x: x + 2
    assert set(callables(f).keys()) == {'bar', 'cbar', 'c', 'sbar'}
    assert set(callables(Foo).keys()) == {'bar', 'cbar', 'sbar'}

def test_nearest_base():
    from syn.base_utils import nearest_base

    class A(object):
        pass

    class B(A):
        pass

    class C(B):
        pass

    class D(object):
        pass

    assert nearest_base(C, [A, B, C]) is C
    assert nearest_base(C, [A, B]) is B
    assert nearest_base(C, [A]) is A
    assert nearest_base(C, [D]) is None
    assert nearest_base(D, [A, B, C]) is None

def test_get_typename():
    from syn.base_utils import get_typename

    class Foo(object):
        pass

    assert get_typename(Foo) == 'Foo'
    assert get_typename(Foo()) == 'Foo'

def test_get_fullname():
    from syn.base_utils import get_fullname
    from syn.base.a import Base

    assert get_fullname(Base) == 'syn.base.a.base.Base'
    assert get_fullname(Base()) == 'syn.base.a.base.Base'

def test_same_lineage():
    from syn.base_utils import same_lineage

    class A(object): pass
    class B(object): pass
    class A1(A): pass
    class A2(A): pass
    class A11(A1): pass

    assert not same_lineage(A, B)
    assert not same_lineage(A(), B())
    assert_raises(TypeError, same_lineage, A, B())
    assert_raises(TypeError, same_lineage, A(), B)

    assert same_lineage(A, A)
    assert same_lineage(A, A1)
    assert same_lineage(A1, A11)

    assert not same_lineage(A11, A2)

def test_type_partition():
    from syn.base_utils import type_partition

    l = [1, 3.4, 5, 'a', 6.7, 'b', 8, {}]
    assert type_partition(l) == {int: [1, 5, 8],
                                 float: [3.4, 6.7],
                                 str: ['a', 'b'],
                                 dict: [{}]}
    assert type_partition(l, int, float) == {int: [1, 5, 8],
                                             float: [3.4, 6.7],
                                             None: ['a', 'b', {}]}

#-------------------------------------------------------------------------------
# Object utilities

def test_rgetattr():
    from syn.base_utils import rgetattr, AttrDict
    obj = AttrDict(a = AttrDict(b = AttrDict(c = 1,
                                             d = 2),
                                e = AttrDict(f = 3)),
                   g = 4)
    
    assert rgetattr(obj, 'a.b.c') == 1
    assert rgetattr(obj, 'a.b.d') == 2
    assert rgetattr(obj, 'a.e.f') == 3
    assert rgetattr(obj, 'a.b.f', 7) == 7

    assert rgetattr(obj, 'g') == 4
    assert rgetattr(obj, 'g', 5) == 4
    assert rgetattr(obj, 'h', 5) == 5

    assert_raises(TypeError, rgetattr, obj, 'a', 3, 4)
    assert_raises(AttributeError, rgetattr, obj, 'h')

def test_safe_vars():
    from syn.base_utils import safe_vars

    class Foo(object):
        pass

    f = Foo()
    f.a = 1
    assert safe_vars(f) == dict(a = 1)
    assert safe_vars(1) == {}

#-------------------------------------------------------------------------------
# Function utilities

def test_compose():
    from syn.base_utils import compose

    def f(x): return x + 2
    def g(x): return 2 * x
    def h(x): return x - 2

    f1 = compose(g, f)
    f2 = compose(f, g)
    f3 = compose(f, g, h)

    assert f1(3) == 10
    assert f2(3) == 8
    assert f3(3) == 4

def test_full_funcname():
    from syn.base_utils import full_funcname, REPL, this_module
    
    class Foo(object):
        @classmethod
        def bar(cls):
            pass
        @staticmethod
        def baz():
            pass

    Foo.bar()
    Foo.baz()

    r = REPL()
    s = set([1, 2, 3])
    modname = this_module().__name__

    assert full_funcname(full_funcname) == 'syn.base_utils.py.full_funcname'
    assert full_funcname(r.eval) == 'syn.base_utils.repl.REPL.eval'
    if six.PY2:
        assert_raises(TypeError, full_funcname, REPL.eval)
    else:
        assert full_funcname(REPL.eval) == 'syn.base_utils.repl.eval'
    assert full_funcname(Foo.bar) == '{}.Foo.bar'.format(modname)
    assert full_funcname(Foo.baz) == '{}.baz'.format(modname)

    if six.PY2:
        assert full_funcname(s.__contains__) == '__builtin__.set.__contains__'
    else:
        assert full_funcname(s.__contains__) == 'builtins.set.__contains__'
        
def test_hangwatch():
    from syn.base_utils import hangwatch, message
    from time import sleep

    accum = []
    assert sum(accum) == 0

    def thing1():
        accum.append(1)
    
    hangwatch(1, thing1)
    assert sum(accum) == 1

    def thing2():
        sleep(.05)

    assert_raises(RuntimeError, hangwatch, .01, thing2)

    def thing3(msg='foo'):
        raise NotImplementedError(msg)

    with capture():
        assert_raises(NotImplementedError, hangwatch, 1, thing3)

    try:
        with capture():
            hangwatch(1, thing3, 'bar')
    except NotImplementedError as e:
        assert message(e) == 'bar'

#-------------------------------------------------------------------------------
# Sequence utilities

def test_index():
    from syn.base_utils import index
    
    lst = list(range(10))
    assert index(lst, 0) == 0
    assert index(lst, 9) == 9
    assert index(lst, 10) is None

def test_unzip():
    from syn.base_utils import unzip

    assert list(unzip(((1, 2), (3, 4)))) == [(1, 3), (2, 4)]
    assert list(unzip(((x, 2*x) for x in range(1, 4)))) == [(1, 2, 3), (2, 4, 6)]

def test_tuple_append():
    from syn.base_utils import tuple_append

    t = (1, 2, 3)
    t2 = tuple_append(t, 4)
    assert t2 == (1, 2, 3, 4)

def test_tuple_prepend():
    from syn.base_utils import tuple_prepend

    t = (1, 2, 3)
    t2 = tuple_prepend(4, t)
    assert t2 == (4, 1, 2, 3)

#-------------------------------------------------------------------------------
# Mapping utilities

def test_getitem():
    from syn.base_utils import getitem

    dct = dict(a = 1, b = 1.2, c = 'abc')
    for key, val in dct.items():
        assert getitem(dct, key) == val
    
    ukey = 'd'
    uval = 5
    assert ukey not in dct
    
    assert_raises(KeyError, getitem, dct, ukey)
    assert_raises(KeyError, getitem, dct, ukey, None)
    assert getitem(dct, ukey, uval) == uval
    assert getitem(dct, ukey, None, True) is None

    assert getitem(dct, 'c', delete=True) == 'abc'
    assert 'c' not in dct

#-------------------------------------------------------------------------------
# Module utilities

def test_get_mod():
    from syn.base_utils import get_mod
    from syn.base.a import Base

    assert get_mod(Base) == 'syn.base.a.base'
    assert get_mod(Base()) == 'syn.base.a.base'

def test_import_module():
    import os
    import os.path

    m2 = import_module('os.path')
    assert vars(m2).keys() == vars(os.path).keys()

    m3 = import_module('os')
    assert vars(m3).keys() == vars(os).keys()

def test_this_module():
    from syn.base_utils import this_module

    this = this_module()
    assert hasattr(this, 'test_this_module')
    assert hasattr(this, 'test_import_module')
    assert this.test_this_module is test_this_module

def test_harvest_metadata():
    from syn.base_utils import harvest_metadata
    from . import harvest1 as h1

    assert h1.__a__ == 1
    assert h1.__b__ == 2.3
    assert h1.__c__ == 'abc'
    assert h1.__d__ is False
    assert h1.__version__ == '1.0'

    assert h1.harvest_metadata is harvest_metadata

#-------------------------------------------------------------------------------
# Exception utilities

def test_message():
    e = TypeError('err')
    assert message(e) == 'err'
    assert message(TypeError()) == ''

#-------------------------------------------------------------------------------
# Unit Test Collection

def test_run_all_tests():
    from syn.base_utils import run_all_tests

    var1 = [1]
    var2 = [2]
    var3 = [3]
    var4 = [4]

    def test():
        var1.append(5)
    def test_blah_blah():
        var2.append(6)
    def blank_test():
        var3.append(7)
    def some_other_func():
        var4.append(8)
        
    assert 'run_all_tests' in locals()
    with assign(sys, 'argv', []):
        with capture() as (out, err):
            run_all_tests(locals(), verbose=True)
            assert out.getvalue() == 'blank_test\ntest\ntest_blah_blah\n'
            assert err.getvalue() == ''

    assert var1 == [1,5]
    assert var2 == [2,6]
    assert var3 == [3,7]
    assert var4 == [4]

    with assign(sys, 'argv', ['', '', '--include', 
                              'test,test_blah_blah,some_other_func']):
        with capture() as (out, err):
            run_all_tests(locals(), verbose=True)
            assert out.getvalue() == 'test\ntest_blah_blah\n'
            assert err.getvalue() == ''
    
    assert var1 == [1,5,5]
    assert var2 == [2,6,6]
    assert var3 == [3,7]
    assert var4 == [4]

    some_other_func()
    assert var4 == [4,8]

    def test_error_func():
        raise TypeError('Testing exception trace printing')

    with assign(sys, 'argv', []):
        with capture() as (out, err):
            run_all_tests(locals(), verbose=True, print_errors=True)
            assert out.getvalue() == ('blank_test\ntest\ntest_blah_blah\n'
                                      'test_error_func\n')
            assert err.getvalue().split('\n')[-2] == \
                'TypeError: Testing exception trace printing'

    with assign(sys, 'argv', ['--print-errors']):
        with capture() as (out, err):
            run_all_tests(locals(), verbose=True, print_errors=False)
            assert out.getvalue() == ('blank_test\ntest\ntest_blah_blah\n'
                                      'test_error_func\n')
            assert err.getvalue().split('\n')[-2] == \
                'TypeError: Testing exception trace printing'

    with assign(sys, 'argv', []):
        with capture() as (out, err):
            assert_raises(TypeError, run_all_tests, locals(), verbose=True, 
                          print_errors=False)

#-------------------------------------------------------------------------------
# Testing utilities


class EquivObj(object):
    def __init__(self, value):
        self.value = value
    def __eq__(self, x):
        return (self.value == x.value)

class EquivObj2(EquivObj):
    pass

class DeepcopyEquivObj(EquivObj):
    def __deepcopy__(self, memo):
        return self
    
class PickleEquivObj(EquivObj):
    def __getstate__(self):
        state = dict(value = self.value + 1)
        return state

    def __setstate__(self, state):
        self.value = state['value']
    

def test_assert_equivalent():
    from syn.base_utils import assert_equivalent

    e1 = EquivObj(1)
    e2 = EquivObj(1)
    e3 = EquivObj(2)

    assert_equivalent(e1, e2)
    assert_raises(AssertionError, assert_equivalent, e1, e3)
    assert_raises(AssertionError, assert_equivalent, e2, e3)
    assert_raises(AssertionError, assert_equivalent, e1, e1)

def test_assert_inequivalent():
    from syn.base_utils import assert_inequivalent

    e1 = EquivObj(1)
    e2 = EquivObj(1)
    e3 = EquivObj(2)

    assert_raises(AssertionError, assert_inequivalent, e1, e2)
    assert_inequivalent(e1, e3)
    assert_inequivalent(e2, e3)
    assert_raises(AssertionError, assert_inequivalent, e1, e1)

def test_assert_type_equivalent():
    from syn.base_utils import assert_type_equivalent, assert_equivalent
    from syn.base_utils.dict import AttrDict

    e1 = EquivObj(1)
    e2 = EquivObj(1)
    e3 = EquivObj2(1)

    assert_type_equivalent(e1, e2)
    assert_equivalent(e1, e3)
    assert_raises(AssertionError, assert_type_equivalent, e1, e3)

    d1 = dict(a = 1, b = 2)
    d2 = AttrDict(a = 1, b = 2)

    assert_equivalent(d1, d2)
    assert_raises(AssertionError, assert_type_equivalent, d1, d2)

def test_assert_deepcopy_idempotent():
    from syn.base_utils import assert_deepcopy_idempotent

    e1 = EquivObj(1)
    e2 = DeepcopyEquivObj(1)

    assert_deepcopy_idempotent(e1)
    assert_raises(AssertionError, assert_deepcopy_idempotent, e2)

def test_assert_pickle_idempotent():
    from syn.base_utils import assert_pickle_idempotent

    e1 = EquivObj(1)
    e2 = PickleEquivObj(1)

    assert_pickle_idempotent(e1)
    assert_raises(AssertionError, assert_pickle_idempotent, e2)

def test_elog():
    from syn.base_utils import elog, this_module
    import syn.base_utils.py as sp

    modname = this_module().__name__

    class ElogTest(Exception): pass

    msgs = []
    class FakeLogger(object):
        def error(self, msg):
            msgs.append(msg)
        @classmethod
        def cmeth(cls):
            pass
        @staticmethod
        def smeth():
            pass
            
    
    FakeLogger.cmeth()
    FakeLogger.smeth()

    logger = FakeLogger()
    with assign(sp, 'elogger', logger):
        elog(ElogTest('msg 1'), elog, (1, 1.2, 'abc'))
        assert msgs[-1] == ('***ElogTest***: "msg 1" --- '
                            'syn.base_utils.py.elog(1, 1.2, abc)')

        elog(ElogTest('msg 2'), message, (1, 1.2, 'abc'), dict(a=2, b=3.4))
        assert msgs[-1] == ('***ElogTest***: "msg 2" --- '
                            'syn.base_utils.py.message(1, 1.2, abc, a=2, b=3.4)')

        elog(ElogTest('msg 3'), test_elog, (1, 1.2, 'abc'), dict(a=2), 
             pretty=False)
        assert msgs[-1] == ('***ElogTest***: "msg 3" --- '
                            '{}.test_elog'.format(modname) + 
                            '(args=(1, 1.2, \'abc\'), '
                            'kwargs={\'a\': 2})')

        elog(ElogTest('msg4'), logger.error, ('abc',))
        assert msgs[-1] == ('***ElogTest***: "msg4" --- '
                            '{}.FakeLogger.error(abc)'.format(modname))
                            
        elog(ElogTest('msg5'), FakeLogger.cmeth)
        assert msgs[-1] == ('***ElogTest***: "msg5" --- '
                            '{}.FakeLogger.cmeth()'.format(modname))

        elog(ElogTest('msg6'), FakeLogger.smeth)
        assert msgs[-1] == ('***ElogTest***: "msg6" --- '
                            '{}.smeth()'.format(modname))

        elog(ElogTest('msg7'), FakeLogger.smeth, name='FakeLogger.smeth')
        assert msgs[-1] == ('***ElogTest***: "msg7" --- '
                            '{}.FakeLogger.smeth()'.format(modname))

        elog(ElogTest('msg8'), elog, (1, 1.2, u'ab\u2013cd'))

def test_ngzwarn():
    from syn.base_utils import ngzwarn, this_module
    import syn.base_utils.py as sp

    mod = this_module()

    msgs = []
    class FakeLogger(object):
        def warning(self, msg):
            msgs.append(msg)

    logger = FakeLogger()
    with assign(sp, 'test_logger', logger):
        ngzwarn(1, 'FOO')
        assert msgs == []

        ngzwarn(0, 'Test value 1')
        assert msgs[-1] == ('Test value 1 set to value <= 0 (0) in {}'
                            .format(mod.__name__))

        ngzwarn(-1, 'Test value 2')
        assert msgs[-1] == ('Test value 2 set to value <= 0 (-1) in {}'
                            .format(mod.__name__))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
