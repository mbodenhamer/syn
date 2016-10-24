import os
import sys
import threading
from syn.five import STR, PY2
from collections import Iterable
from six.moves import cStringIO
from contextlib import contextmanager
from syn.globals import SUPPRESS_TEST_ERRORS

#-------------------------------------------------------------------------------
# null_context

@contextmanager
def null_context():
    '''A context manager that does nothing.
    '''
    yield

#-------------------------------------------------------------------------------
# Temporary assignment

@contextmanager
def assign(A, attr, B, lock=False):
    '''Assigns B to A.attr, yields, and then assigns A.attr back to its
    original value.
    '''
    class NoAttr(object): pass

    context = threading.Lock if lock else null_context
    with context():
        if not hasattr(A, attr):
            tmp = NoAttr
        else:
            tmp = getattr(A, attr)

        setattr(A, attr, B)

        try:
            yield B

        finally:
            if tmp is NoAttr:
                delattr(A, attr)
            else:
                setattr(A, attr, tmp)

#-------------------------------------------------------------------------------
# Temporary item assignment

@contextmanager
def setitem(dct, name, item, lock=False):
    class NoItem(object): pass

    context = threading.Lock if lock else null_context
    with context():
        if name not in dct:
            tmp = NoItem
        else:
            tmp = dct[name]

        dct[name] = item

        try:
            yield item

        finally:
            if tmp is NoItem:
                del dct[name]
            else:
                dct[name] = tmp

#-------------------------------------------------------------------------------
# cd

@contextmanager
def chdir(path):
    with threading.Lock():
        pwd = os.getcwd()
        os.chdir(path)

        try:
            yield
        finally:
            os.chdir(pwd)

#-------------------------------------------------------------------------------
# delete

@contextmanager
def delete(*args):
    '''For using then deleting objects.'''
    from syn.base_utils import this_module
    mod = this_module(npop=3)
    yield
    for arg in args:
        name = arg
        if not isinstance(name, STR):
            name = arg.__name__
        delattr(mod, name)

#-------------------------------------------------------------------------------
# nested_context

@contextmanager
def nested_context(contexts, argss=None, kwargss=None, extend=False):
    from .py import getitem
    argss = argss if argss else []
    kwargss = kwargss if kwargss else []

    gens = []
    rets = []
    for k, context in enumerate(contexts):
        args = getitem(argss, k, ())
        kwargs = getitem(kwargss, k, {})
        gen = context(*args, **kwargs)
        gens.append(gen)
        ret = gen.__enter__()
        if ret:
            if isinstance(ret, Iterable) and extend:
                rets.extend(ret)
            else:
                rets.append(ret)

    err = None
    exc_info = (None, None, None)
    try:
        yield tuple(rets)
    except Exception as err:
        exc_info = sys.exc_info()

    for gen in reversed(gens):
        gen.__exit__(*exc_info)

    if PY2:
        if err:
            raise err

#-------------------------------------------------------------------------------
# capture

@contextmanager
def capture(names=('stdout', 'stderr'), obj=sys, typ=cStringIO):
    argss = []
    for name in names:
        argss.append((obj, name, typ()))

    contexts = [assign] * len(names)
    with nested_context(contexts, argss) as ret:
        yield ret

#-------------------------------------------------------------------------------
# on_error

@contextmanager
def on_error(func, *args, **kwargs):
    from .py import getitem

    suppress = False
    if '___suppress_errors' in kwargs:
        suppress = getitem(kwargs, '___suppress_errors', delete=True)
    elif getitem(kwargs, '___suppress_global', True, delete=True):
        suppress = SUPPRESS_TEST_ERRORS

    try:
        yield
    except Exception as e:
        func(e, *args, **kwargs)
        if not suppress:
            raise e

#-------------------------------------------------------------------------------
# __all__

__all__ = ('null_context', 'assign', 'setitem', 'chdir', 'delete', 
           'nested_context', 'capture', 'on_error')

#-------------------------------------------------------------------------------
