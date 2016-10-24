import os
import sys
from copy import copy
from functools import partial
from nose.tools import assert_raises
from contextlib import contextmanager
from syn.base_utils import message

DIR = os.path.dirname(os.path.abspath(__file__))
FOO = os.path.join(DIR, 'foo')

#-------------------------------------------------------------------------------
# null_context

def test_null_context():
    from syn.base_utils import null_context

    l = [1, 2, 3]
    with null_context():
        assert l == [1, 2, 3]

#-------------------------------------------------------------------------------
# Temporary assignment

def test_assign():
    from syn.base_utils import assign

    class Foo(object):
        lst = [1, 2, 3]

    assert Foo.lst == [1, 2, 3]

    with assign(Foo, 'lst', [3, 4, 5]) as lst:
        assert Foo.lst == [3, 4, 5]
        assert lst is Foo.lst
    assert Foo.lst == [1, 2, 3]

    with assign(Foo, 'lst', [3, 4, 5], lock=True):
        assert Foo.lst == [3, 4, 5]
    assert Foo.lst == [1, 2, 3]

    assert not hasattr(Foo, 'a')
    with assign(Foo, 'a', 1):
        assert hasattr(Foo, 'a')
        assert Foo.a == 1
    assert not hasattr(Foo, 'a')

    def exc():
        with assign(Foo, 'a', 1):
            assert Foo.a == 1
            raise RuntimeError

    assert_raises(RuntimeError, exc)
    assert not hasattr(Foo, 'a')

#-------------------------------------------------------------------------------
# Temporary item assignment

def test_setitem():
    from syn.base_utils import setitem

    dct = dict(a = 1, b = 2)
    cdct = copy(dct)
    
    assert dct == cdct
    with setitem(dct, 'a', 3):
        assert dct == dict(a = 3, b = 2)
    assert dct == cdct

    assert 'c' not in dct
    with setitem(dct, 'c', 4) as x:
        assert x == 4
        assert dct == dict(a = 1, b = 2, c = 4)
    assert 'c' not in dct
    assert dct == cdct

    def exc():
        with setitem(dct, 'c', 4):
            assert dct['c'] == 4
            raise RuntimeError

    assert_raises(RuntimeError, exc)
    assert 'c' not in dct

#-------------------------------------------------------------------------------
# cd

def test_chdir():
    from syn.base_utils import chdir

    pwd = os.getcwd()
    assert pwd != FOO
    with chdir(FOO):
        assert os.getcwd() == FOO != pwd
        with open('foo', 'rt') as f:
            assert f.read() == 'foo'
    assert pwd == os.getcwd() != FOO

#-------------------------------------------------------------------------------
# delete

def test_delete():
    from . import delete1 as d1

    assert d1.__a__ == 1
    assert d1.__b__ == 2.3
    assert d1.__c__ == 'abc'
    assert d1.__d__ is False
    assert d1.__version__ == '1.0'

    assert not hasattr(d1, 'delete')
    assert not hasattr(d1, 'harvest_metadata')

#-------------------------------------------------------------------------------
# nested_context

def test_nested_context():
    from syn.base_utils import nested_context, assign

    class Foo(object):
        pass

    assert not hasattr(Foo, 'a')
    assert not hasattr(Foo, 'b')

    with nested_context([assign]*2, [(Foo, 'a', 1),
                                     (Foo, 'b', 2)]):
        assert Foo.a == 1
        assert Foo.b == 2

    assert not hasattr(Foo, 'a')
    assert not hasattr(Foo, 'b')

    @contextmanager
    def plus1(x):
        yield x+1

    @contextmanager
    def plus2(x):
        yield x+2

    @contextmanager
    def plus3(x):
        yield x+3

    x = 1
    with nested_context([partial(plus1, x),
                         partial(plus2, x),
                         partial(plus3, x)]) as (w, y, z):
        assert x == 1
        assert w == 2
        assert y == 3
        assert z == 4
    
    @contextmanager
    def bad(x):
        raise TypeError('a really really bad error')

    @contextmanager
    def terrible(x):
        if False:
            yield # pragma: no cover

    try:
        with nested_context([plus1, bad], [[x]]*2) as (y, z): pass
    except TypeError as e:
        assert message(e) == 'a really really bad error'

    try:
        with nested_context([plus1, terrible], [[x]]*2) as (y, z): pass
    except RuntimeError as e:
        assert message(e) == "generator didn't yield"

    try:
        with nested_context([plus1, plus2], [[5]]*2) as (y, z):
            assert y == 6
            assert z == 7
            raise TypeError('foobarbaz')
    except TypeError as e:
        assert message(e) == 'foobarbaz'

    @contextmanager
    def listy(x):
        yield [x]*x

    with nested_context([listy, listy], [[1], [2]]) as ret:
        assert ret == ([1], [2, 2])

    with nested_context([listy, listy], [[1], [2]], extend=True) as ret:
        assert ret == (1, 2, 2)

#-------------------------------------------------------------------------------
# capture

def test_capture():
    from syn.base_utils import capture, assign
    from six.moves import cStringIO

    oout = cStringIO()
    oerr = cStringIO()

    with assign(sys, 'stdout', oout):
        with assign(sys, 'stderr', oerr):
            print("Outside")
            sys.stderr.write('Err1\n')
            with capture() as (out, err):
                print("Inside")
                sys.stderr.write('Err!\n')

                assert out.getvalue() == 'Inside\n'
                assert err.getvalue() == 'Err!\n'

            print("Outside2")
            sys.stderr.write('Err2\n')

            assert out.getvalue() == 'Inside\n'
            assert err.getvalue() == 'Err!\n'
            
    print("Outside")
    
    assert oout.getvalue() == 'Outside\nOutside2\n'
    assert oerr.getvalue() == 'Err1\nErr2\n'

#-------------------------------------------------------------------------------
# on_error

def test_on_error():
    from syn.base_utils import on_error, getitem

    accum = []
    def add(exc, *args, **kwargs):
        x = getitem(args, 0, 1)
        accum.append(x)

    def test():
        with on_error(add, 2, ___suppress_global=False):
            raise RuntimeError

    assert sum(accum) == 0
    add(Exception())
    assert sum(accum) == 1

    assert_raises(RuntimeError, test)
    assert sum(accum) == 3


    def test2():
        with on_error(add, 3, ___suppress_errors=True):
            raise RuntimeError

    test2()
    assert sum(accum) == 6

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
