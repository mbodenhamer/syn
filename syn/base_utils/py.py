import re
import os
import six
import sys
import yaml
import types
import inspect
import logging
import threading
import traceback
from six.moves.queue import Queue
from collections import defaultdict
from functools import reduce, partial
from syn.globals import test_logger

#-------------------------------------------------------------------------------

import six.moves.builtins
builtins = list(vars(six.moves.builtins).values())

# NOTE: for classes only (not objects)
if six.PY2:
    METHOD_TYPES = (types.MethodType, types.BuiltinMethodType)
else:
    METHOD_TYPES = (types.MethodType, types.BuiltinMethodType,
                    types.FunctionType, types.BuiltinFunctionType)

#-------------------------------------------------------------------------------
# elogger setup

elogger = logging.getLogger('elog')
elogger_handler = logging.StreamHandler()
elogger_handler.setFormatter(logging.Formatter('[elog] %(message)s'))
elogger.addHandler(elogger_handler)
elogger.setLevel(logging.ERROR)

#-------------------------------------------------------------------------------
# Printing utilities

def eprint(out, flush=True):
    if not out.endswith('\n'):
        out += '\n'
    sys.stderr.write(out)
    if flush:
        sys.stderr.flush()

#-------------------------------------------------------------------------------
# Class utilities

def subclasses(cls, lst=None):
    '''Recursively gather subclasses of cls.
    '''
    if lst is None:
        lst = []
    for sc in cls.__subclasses__():
        if sc not in lst:
            lst.append(sc)
        subclasses(sc, lst=lst)
    return lst

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

def is_subclass(x, typ):
    if not isinstance(x, type):
        return False
    return issubclass(x, typ)

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

def get_fullname(x):
    return '{}.{}'.format(get_mod(x), get_typename(x))

def same_lineage(o1, o2):
    '''Returns True iff o1 and o2 are of the same class lineage (that is, a direct line of descent, without branches).'''
    def comp(x, y):
        return issubclass(x, y) or issubclass(y, x)

    if isinstance(o1, type) and isinstance(o2, type):
        return comp(o1, o2)
    elif not (isinstance(o1, type) or isinstance(o2, type)):
        return comp(type(o1), type(o2))
    raise TypeError("Cannot compare type and object")

def type_partition(lst, *types):
    ret = defaultdict(list)
    for item in lst:
        if not types:
            ret[type(item)].append(item)
            continue

        matched = False
        for typ in types:
            if isinstance(item, typ):
                ret[typ].append(item)
                matched = True
                break
        if not matched:
            ret[None].append(item)
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

def safe_vars(*args, **kwargs):
    try:
        return vars(*args, **kwargs)
    except TypeError:
        return {}

#-------------------------------------------------------------------------------
# Function utilities

def compose(*funcs):
    return reduce(lambda f, g: lambda x: f(g(x)), funcs, lambda x: x)

def full_funcname(func):
    name = func.__name__

    if hasattr(func, '__self__'):
        if func.__self__ is None:
            raise TypeError('Attempted to get name of unbound method {}'
                            .format(func))
        name = '{}.{}'.format(get_typename(func.__self__), name)
        return '{}.{}'.format(get_mod(func.__self__), name)
    return '{}.{}'.format(get_mod(func), name)

def hangwatch(timeout, func, *args, **kwargs):
    def target(queue):
        try:
            func(*args, **kwargs)
        except Exception as e:
            queue.put(sys.exc_info())
            queue.put(e)
            sys.exit()

    q = Queue()
    thread = threading.Thread(target=target, args = (q,))
    
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        raise RuntimeError('Operation did not terminate within {} seconds'
                           .format(timeout))

    if not q.empty():
        info = q.get(block=False)
        e = q.get(block=False)
        eprint(''.join(traceback.format_exception(*info)))
        raise e

#-------------------------------------------------------------------------------
# Sequence utilities

def index(seq, elem):
    if elem in seq:
        return seq.index(elem)
    return None

def unzip(seq):
    return zip(*list(seq))

def tuple_append(tup, x):
    ret = tup + (x,)
    return ret

def tuple_prepend(x, tup):
    ret =  (x,) + tup
    return ret

#-------------------------------------------------------------------------------
# Mapping utilities

def getitem(mapping, item, default=None, allow_none_default=False, delete=False):
    try:
        ret = mapping[item]
    except (KeyError, IndexError) as e:
        if default is not None or allow_none_default:
            return default
        raise e
    
    if delete:
        del mapping[item]
    return ret

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

def this_module(npop=1):
    '''Returns the module object of the module this function is called from
    '''
    stack = inspect.stack()
    st = stack[npop]
    frame = st[0]
    return inspect.getmodule(frame)

that_module = partial(this_module, npop=2)

def harvest_metadata(fpath, abspath=False, template='__{}__'):
    mod = that_module()
    path = fpath
    if not abspath:
        path = os.path.join(os.path.dirname(os.path.abspath(mod.__file__)),
                            path)

    with open(path, 'r') as f:
        for key, value in yaml.load(f).items():
            setattr(mod, template.format(key), value)

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

def run_all_tests(env, verbose=False, print_errors=False, exclude=None,
                  include=None):
    import sys
    import traceback

    exclude = exclude if exclude else []
    include = include if include else []

    include = []
    if '--include' in sys.argv:
        idx = sys.argv.index('--include')
        include = sys.argv[idx+1].split(',')

    if '--print-errors' in sys.argv:
        print_errors = True

    testfuncs = []
    for key in env:
        if key != 'run_all_tests':
            if key not in exclude:
                if _identify_testfunc(key):
                    if hasattr(env[key], '__call__'):
                        if isinstance(env[key], types.FunctionType):
                            testfuncs.append(key)

    if include:
        testfuncs = set(testfuncs).intersection(set(include))

    for tf in sorted(testfuncs):
        if verbose:
            print(tf)
        if print_errors:
            try:
                env[tf]()
            except:
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

def elog(exc, func, args=None, kwargs=None, str=str, pretty=True, name=''):
    '''For logging exception-raising function invocations during randomized unit tests.
    '''
    from .str import safe_str

    args = args if args else ()
    kwargs = kwargs if kwargs else {}
    name = '{}.{}'.format(get_mod(func), name) if name else full_funcname(func)

    if pretty:
        invocation = ', '.join([safe_str(arg) for arg in args])
        if kwargs:
            invocation += ', '
            invocation += ', '.join(['{}={}'.format(key, safe_str(value))
                                     for key, value in sorted(kwargs.items())])
    else:
        invocation = 'args={}, kwargs={}'.format(safe_str(args), safe_str(kwargs))

    msg = '***{}***: "{}" --- {}({})'.format(get_typename(exc),
                                             message(exc),
                                             name,
                                             invocation)
    elogger.error(msg)

def ngzwarn(value, name):
    if value <= 0:
        mod = that_module()
        msg = '{} set to value <= 0 ({}) in {}'.format(name, value, mod.__name__)
        test_logger.warning(msg)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('mro', 'hasmethod', 'import_module', 'message', 'run_all_tests',
           'index', 'nearest_base', 'get_typename', 'get_mod', 'compose',
           'assert_equivalent', 'assert_inequivalent', 'assert_type_equivalent',
           'assert_pickle_idempotent', 'assert_deepcopy_idempotent',
           'rgetattr', 'callables', 'is_subclass', 'getitem', 'same_lineage',
           'type_partition', 'subclasses', 'unzip', 'this_module',  'eprint',
           'that_module', 'harvest_metadata', 'tuple_append', 'get_fullname',
           'tuple_prepend', 'elog', 'ngzwarn', 'full_funcname', 'hangwatch',
           'safe_vars',)

#-------------------------------------------------------------------------------
