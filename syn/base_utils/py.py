import re
import six
import types
import inspect
from functools import reduce

#-------------------------------------------------------------------------------

import six.moves.builtins # pylint: disable=E0401
builtins = list(vars(six.moves.builtins).values())

# NOTE: for classes only (not objects)
if six.PY2:
    METHOD_TYPES = (types.MethodType, types.BuiltinMethodType)
else:
    METHOD_TYPES = (types.MethodType, types.BuiltinMethodType,
                    types.FunctionType, types.BuiltinFunctionType)

#-------------------------------------------------------------------------------
# Class utilities

def mro(cls):
    if cls is type:
        return [type]
    elif isinstance(cls, type):
        try:
            return cls.mro()
        except TypeError:
            return [cls]
    else:
        return type(cls).mro()

def hasmethod(x, name):
    val = getattr(x, name, None)
    if isinstance(x, type):
        return isinstance(val, METHOD_TYPES)
    return inspect.ismethod(val)

def callables(obj, exclude_sys=True):
    dct = dict(inspect.getmembers(obj))

    if exclude_sys:
        dct = {key: val for key,val in dct.items() if not
               key.startswith('__')}

    ret = {key: val for key,val in dct.items() if hasattr(val, '__call__')}
    return ret

def nearest_base(cls, bases):
    '''Returns the closest ancestor to cls in bases.
    '''
    if cls in bases:
        return cls

    dists = {base: index(mro(cls), base) for base in bases}
    dists2 = {dist: base for base, dist in dists.items() if dist is not None}
    if not dists2:
        return None
    return dists2[min(dists2)] 

def get_typename(x):
    '''Returns the name of the type of x, if x is an object.  Otherwise, returns the name of x.
    '''
    if isinstance(x, type):
        ret = x.__name__
    else:
        ret = x.__class__.__name__
    return ret

#-------------------------------------------------------------------------------
# Object utilities

def rgetattr(obj, attr, *args):
    if args:
        default = args[0]
        default_given = True
        if len(args) > 1:
            raise TypeError("rgetattr() takes at most 3 arguments; "
                            "{} given".format(len(args) + 2))
    else:
        default = None
        default_given = False

    attrs = attr.split('.')
    attr = attrs[0]
    rest = '.'.join(attrs[1:])

    if hasattr(obj, attr):
        value = getattr(obj, attr)
        if rest:
            return rgetattr(value, rest, *args)
        return value

    if default_given:
        return default
    raise AttributeError("Cannot resolve {}.{}".format(obj, attr))

#-------------------------------------------------------------------------------
# Function utilities

def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, lambda x: x)

#-------------------------------------------------------------------------------
# Sequence utilities

def index(seq, elem):
    if elem in seq:
        return seq.index(elem)
    return None

#-------------------------------------------------------------------------------
# Module utilities

def get_mod(cls):

    '''Returns the string identifying the module that cls is defined in.
    '''
    if isinstance(cls, (type, types.FunctionType)):
        ret = cls.__module__
    else:
        ret = cls.__class__.__module__
    return ret

def import_module(modname):
    if '.' in modname:
        module = modname.split('.')[-1]
        mod = __import__(modname, fromlist=[module])
    else:
        mod = __import__(modname)
    return mod

#-------------------------------------------------------------------------------
# Exception utilities

def message(e):
    if hasattr(e, 'message'):
        return e.message
    if e.args:
        return e.args[0]
    return ''

#-------------------------------------------------------------------------------
# Unit Test Collection

NOSE_PATTERN = re.compile('(?:^|[\\b_\\.-])[Tt]est')

def _identify_testfunc(s):
    return bool(re.search(NOSE_PATTERN, s))

def run_all_tests(env, verbose=False, print_errors=False, exclude=None):
    import sys
    import traceback

    if exclude is None:
        exclude = []

    testfuncs = []
    for key in env:
        if key != 'run_all_tests':
            if key not in exclude:
                if _identify_testfunc(key):
                    if hasattr(env[key], '__call__'):
                        if isinstance(env[key], types.FunctionType):
                            testfuncs.append(key)

    for tf in testfuncs:
        if verbose:
            print(tf)
        if print_errors:
            try:
                env[tf]()
            except: # pylint: disable=W0702
                traceback.print_exception(*sys.exc_info())
        else:
            env[tf]()
        
#-------------------------------------------------------------------------------
# Testing utilities

def assert_equivalent(o1, o2):
    '''Asserts that o1 and o2 are distinct, yet equivalent objects
    '''
    if not (isinstance(o1, type) and isinstance(o2, type)):
        assert o1 is not o2
    assert o1 == o2
    assert o2 == o1

def assert_inequivalent(o1, o2):
    '''Asserts that o1 and o2 are distinct and inequivalent objects
    '''
    if not (isinstance(o1, type) and isinstance(o2, type)):
        assert o1 is not o2
    assert not o1 == o2 and o1 != o2
    assert not o2 == o1 and o2 != o1

def assert_type_equivalent(o1, o2):
    '''Asserts that o1 and o2 are distinct, yet equivalent objects of the same type
    '''
    assert o1 == o2
    assert o2 == o1
    assert type(o1) is type(o2)

def assert_deepcopy_idempotent(obj):
    '''Assert that obj does not change (w.r.t. ==) under repeated deepcopies
    '''
    from copy import deepcopy
    obj1 = deepcopy(obj)
    obj2 = deepcopy(obj1)
    obj3 = deepcopy(obj2)
    assert_equivalent(obj, obj1)
    assert_equivalent(obj, obj2)
    assert_equivalent(obj, obj3)
    assert type(obj) is type(obj3)

def assert_pickle_idempotent(obj):
    '''Assert that obj does not change (w.r.t. ==) under repeated picklings
    '''
    from six.moves.cPickle import dumps, loads
    obj1 = loads(dumps(obj))
    obj2 = loads(dumps(obj1))
    obj3 = loads(dumps(obj2))
    assert_equivalent(obj, obj1)
    assert_equivalent(obj, obj2)
    assert_equivalent(obj, obj3)
    assert type(obj) is type(obj3)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('mro', 'hasmethod', 'import_module', 'message', 'run_all_tests',
           'index', 'nearest_base', 'get_typename', 'get_mod', 'compose',
           'assert_equivalent', 'assert_inequivalent', 'assert_type_equivalent',
           'assert_pickle_idempotent', 'assert_deepcopy_idempotent',
           'rgetattr', 'callables')

#-------------------------------------------------------------------------------
