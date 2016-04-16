import re
import six
import types
import inspect

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

#-------------------------------------------------------------------------------
# Module utilities

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
# __all__

__all__ = ('mro', 'hasmethod', 'import_module', 'message', 'run_all_tests')

#-------------------------------------------------------------------------------
