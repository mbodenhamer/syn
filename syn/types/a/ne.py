import collections
import operator as op
from functools import partial
from syn.five import unicode, xrange, izip, STR, NUM
from syn.base_utils import REPL, repl_command, DefaultList, sgn, AttrDict, \
    implies, feq, cfeq, tuple_append
from syn.base_utils.float import DEFAULT_TOLERANCE
from syn.base_utils.rand import PRIMITIVE_TYPES

CONTAINERS = (collections.Mapping, collections.Sequence, set, frozenset)

#-------------------------------------------------------------------------------
# NEType


class NEType(object):
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def __call__(self):
        print(self.message())
        self.explorer()()

    def __eq__(self, other):
        return (self.A == other.A and self.B == other.B and 
                type(self) is type(other))

    def __ne__(self, other):
        return not (self == other)

    def __str__(self):
        try:
            return self.message()
        except NotImplementedError:
            return repr(self)

    def explorer(self):
        xA = ValueExplorer(self.A)
        xB = ValueExplorer(self.B)
        return DiffExplorer(xA, xB)

    def message(self):
        raise NotImplementedError

#-----------------------------------------------------------


class NotEqual(NEType):
    def message(self):
        return '{} != {}'.format(self.A, self.B)


#-----------------------------------------------------------


class DiffersAtIndex(NEType):
    def __init__(self, A, B, index):
        super(DiffersAtIndex, self).__init__(A, B)
        self.index = index

    def __eq__(self, other):
        if not super(DiffersAtIndex, self).__eq__(other):
            return False
        return self.index == other.index

    def explorer(self):
        xA = ValueExplorer(self.A, index=self.index)
        xB = ValueExplorer(self.B, index=self.index)
        return DiffExplorer(xA, xB)

    def message(self):
        iA = self.A[self.index]
        iB = self.B[self.index]
        return ('Sequences differ at index {}: {} != {}'
                .format(self.index, iA, iB))


#-----------------------------------------------------------


class DiffersAtKey(NEType):
    def __init__(self, A, B, key):
        super(DiffersAtKey, self).__init__(A, B)
        self.key = key

    def __eq__(self, other):
        if not super(DiffersAtKey, self).__eq__(other):
            return False
        return self.key == other.key

    def explorer(self):
        xA = ValueExplorer(self.A, key=self.key)
        xB = ValueExplorer(self.B, key=self.key)
        return DiffExplorer(xA, xB)

    def message(self):
        iA = self.A[self.key]
        iB = self.B[self.key]
        return ('Mappings differ at key "{}": {} != {}'
                .format(self.key, iA, iB))


#-----------------------------------------------------------


class DiffersAtAttribute(NEType):
    def __init__(self, A, B, attr):
        super(DiffersAtAttribute, self).__init__(A, B)
        self.attr = attr

    def __eq__(self, other):
        if not super(DiffersAtAttribute, self).__eq__(other):
            return False
        return self.attr == other.attr

    def explorer(self):
        xA = ValueExplorer(self.A, attr=self.attr)
        xB = ValueExplorer(self.B, attr=self.attr)
        return DiffExplorer(xA, xB)

    def message(self):
        iA = getattr(self.A, self.attr)
        iB = getattr(self.B, self.attr)
        return ('Objects differ at attribute "{}": {} != {}'
                .format(self.attr, iA, iB))


#-----------------------------------------------------------


class DifferentLength(NEType):
    def message(self):
        return 'Different lengths: {} != {}'.format(len(self.A), len(self.B))


#-----------------------------------------------------------


class DifferentTypes(NEType):
    def message(self):
        return 'Different types: {} != {}'.format(type(self.A), type(self.B))


#-----------------------------------------------------------


class SetDifferences(NEType):
    def __init__(self, A, B):
        super(SetDifferences, self).__init__(A, B)
        self.diffs = A.difference(B).union(B.difference(A))

    def message(self):
        return 'Exclusive items: {}'.format(self.diffs)


#-----------------------------------------------------------


class KeyDifferences(NEType):
    def __init__(self, A, B):
        super(KeyDifferences, self).__init__(A, B)
        a = set(self.A.keys())
        b = set(self.B.keys())
        self.diffs = a.difference(b).union(b.difference(a))

    def message(self):
        return 'Exclusive keys: {}'.format(self.diffs)


#-------------------------------------------------------------------------------
# ExplorationError


class ExplorationError(Exception):
    pass


#-------------------------------------------------------------------------------
# ValueExplorer


class ValueExplorer(REPL):
    commands = dict(REPL.commands)
    command_help = dict(REPL.command_help)

    def __init__(self, value, index=None, key=None, attr=None, 
                 prompt='(ValEx) ', step=1):
        super(ValueExplorer, self).__init__(prompt)
        self.initial_value = value
        self.initial_index = index
        self.initial_key = key
        self.initial_attr = attr
        self.initial_step_value = step
        self._initialize(value, index, key, attr, prompt, step)

    def _initialize(self, value, index, key, attr, prompt, step):
        # Example
        # self.index = 1
        # self.value = [1, 2, 3, 4]
        # self.current_value = 2
        # But during depth_first, will step down such that index = 0, value = 2

        self.value = value
        self.index = index if index is not None else 0
        self.key = key
        self.attr = attr
        self.step_value = step

        self.stack = DefaultList(None)
        self.stack_index = 0
        self.current_value = None
        self.at_end = False
        self._at_bottom_level()
        self._prime()

    def _at_bottom_level(self):
        self.at_bottom_level = is_visit_primitive(self.value)

    def _check_empty(self):
        if isinstance(self.value, CONTAINERS):
            if len(self.value) == 0 or self.index >= len(self.value):
                self.at_end = True

    def _prime(self):
        from .base import visit
        self.iter = visit(self.value, k=self.index, step=self.step_value, 
                          enumerate=True)

        self._check_empty()
        if not self.at_end:
            if (isinstance(self.value, collections.Mapping) and 
                self.initial_index is None and self.key is not None):
                index, pair = next(self.iter)
                key, value = pair
                while not key == self.key:
                    try:
                        index, pair = next(self.iter)
                        key, value = pair
                    except StopIteration:
                        raise ExplorationError('Unable to find key: {}'
                                               .format(self.key))
                self.current_value = value
                self.index = index

            elif self.initial_index is None and self.attr is not None:
                index, pair = next(self.iter)
                attr, value = pair
                while not attr == self.attr:
                    try:
                        index, pair = next(self.iter)
                        attr, value = pair
                    except StopIteration:
                        raise ExplorationError('Unable to find attribute: {}'
                                               .format(self.attr))
                self.current_value = value
                self.index = index

            else:
                self.step()

    def _pop(self):
        self.stack_index -= 1
        frame = self.stack.pop()
        self.value = frame['value']
        self.current_value = frame['current_value']
        self.index = frame['index']
        self.key = frame['key']
        self.attr = frame['attr']
        self.at_end = frame['at_end']
        self.iter = frame['iter']
        self._at_bottom_level()

    def _push(self):
        frame = dict(value=self.value,
                     current_value=self.current_value,
                     index=self.index,
                     key=self.key,
                     attr=self.attr,
                     iter=self.iter,
                     at_end=self.at_end)
        self.stack_index += 1
        self.stack.append(frame)

        self.value = self.current_value
        self.current_value = None
        self.index = 0
        self.key = None
        self.attr = None
        self.at_end = False
        self._at_bottom_level()
        self._prime()

    def display(self):
        return unicode(self.current_value)

    def step(self, step=None):
        step = int(step) if step is not None else self.step_value
        if step != self.step_value:
            if sgn(step) != sgn(self.step_value):
                if self.at_end:
                    self.at_end = False

            self.step_value = step
            self._prime()

        try:
            index, value = next(self.iter)
            self.index = index

            if isinstance(self.value, collections.Mapping):
                self.key = value[0]
                self.current_value = value[1]
                return

            if isinstance(value, tuple):
                if len(value) == 2:
                    if isinstance(value[0], STR):
                        self.attr = value[0]
                        self.current_value = value[1]
                        return

            self.current_value = value

        except StopIteration:
            self.at_end = True
            raise ExplorationError('At last value')
        
    def down(self):
        if self.at_bottom_level:
            raise ExplorationError('At bottom level')
        self._push()

    def up(self):
        if self.stack_index == 0:
            raise ExplorationError('At top level')
        self._pop()

    def reset(self):
        self._initialize(self.initial_value, self.initial_index,
                         self.initial_key, self.initial_attr, self.prompt, 
                         self.initial_step_value)

    def depth_first(self, leaves_only=False):
        vars = AttrDict(going_up=False,
                        going_forward=False)
        def step():
            try:
                self.step()
            except ExplorationError:
                if self.stack_index > 0:
                    self.up()
                    vars.going_up = True

        if isinstance(self.value, CONTAINERS) and len(self.value) == 0:
            yield self.value

        while True:
            if self.at_end and self.stack_index == 0:
                break

            if not vars.going_up and not vars.going_forward:
                if implies(leaves_only, self.at_bottom_level):
                    yield self.value

            if vars.going_up:
                vars.going_up = False
                vars.going_forward = True
                step()

            elif not self.at_bottom_level:
                vars.going_forward = False
                self.down()

            elif not self.at_end:
                step()
            
    @repl_command('c', 'display current_value')
    def command_display_current_value(self):
        print(self.current_value)

    @repl_command('l', 'display value')
    def command_display_value(self):
        print(self.value)

    @repl_command('d', 'go down the stack')
    def command_down(self, num='1'):
        num = int(num)
        for _ in xrange(num):
            self.down()

    @repl_command('n', 'step')
    def command_step(self, step='1'):
        step = int(step)
        self.step(step)

    @repl_command('u', 'go up the stack')
    def command_up(self, num='1'):
        num = int(num)
        for _ in xrange(num):
            self.up()


#-------------------------------------------------------------------------------
# DiffExplorer


class DiffExplorer(REPL):
    commands = dict(REPL.commands)
    command_help = dict(REPL.command_help)
    
    value = property(lambda self: (self.A.value,
                                   self.B.value))
    current_value = property(lambda self: (self.A.current_value, 
                                           self.B.current_value))

    def __init__(self, A, B, prompt='(DiffEx) '):
        super(DiffExplorer, self).__init__(prompt)
        if not isinstance(A, ValueExplorer):
            A = ValueExplorer(A)
        if not isinstance(B, ValueExplorer):
            B = ValueExplorer(B)

        self.A = A
        self.B = B

    def depth_first(self, **kwargs):
        for a, b in izip(self.A.depth_first(**kwargs), 
                         self.B.depth_first(**kwargs)):
            yield a, b

    def display(self):
        a = self.A.display()
        b = self.B.display()
        return u'A: {}\nB: {}'.format(a, b)

    def step(self, *args, **kwargs):
        self.A.step(*args, **kwargs)
        self.B.step(*args, **kwargs)

    def down(self):
        self.A.down()
        self.B.down()

    def up(self):
        self.A.up()
        self.B.up()

    def reset(self):
        self.A.reset()
        self.B.reset()

    @repl_command('c', 'display current_value')
    def command_display_current_value(self):
        print(self.display())

    @repl_command('l', 'display value')
    def command_display_value(self):
        print("index: " + str(self.A.index))
        if self.A.key:
            print("key: " + str(self.A.key))
        print("A: " + str(self.value[0]))
        print("B: " + str(self.value[1]))

    @repl_command('d', 'go down the stack')
    def command_down(self, num='1'):
        num = int(num)
        for _ in xrange(num):
            self.down()

    @repl_command('n', 'step')
    def command_step(self, step='1'):
        step = int(step)
        self.step(step)

    @repl_command('u', 'go up the stack')
    def command_up(self, num='1'):
        num = int(num)
        for _ in xrange(num):
            self.up()


#-------------------------------------------------------------------------------
# Utilities

def deep_comp(A, B, func=op.eq, **kwargs):
    x = DiffExplorer(A, B)
    for a, b in x.depth_first(**kwargs):
        if not func(a, b):
            return False
    return True

def feq_comp(a, b, tol=DEFAULT_TOLERANCE, relative=True):
    if isinstance(a, STR) or isinstance(b, STR):
        return a == b
    if isinstance(a, CONTAINERS) or isinstance(b, CONTAINERS):
        return type(a) is type(b) and len(a) == len(b)
    if isinstance(a, complex) or isinstance(b, complex):
        return cfeq(a, b, tol, relative)
    return feq(a, b, tol, relative)

def deep_feq(A, B, tol=DEFAULT_TOLERANCE, relative=True):
    if type(A) is not type(B) and not isinstance(A, tuple_append(NUM, complex)):
        return False

    func = partial(feq_comp, tol=tol, relative=relative)
    return deep_comp(A, B, func)

def is_visit_primitive(obj):
    '''Returns true if properly visiting the object returns only the object itself.'''
    from .base import visit
    if (isinstance(obj, tuple(PRIMITIVE_TYPES)) and not isinstance(obj, STR)
        and not isinstance(obj, bytes)):
        return True
    if (isinstance(obj, CONTAINERS) and not isinstance(obj, STR) and not
        isinstance(obj, bytes)):
        return False
    if isinstance(obj, STR) or isinstance(obj, bytes):
        if len(obj) == 1:
            return True
        return False
    return list(visit(obj, max_enum=2)) == [obj]

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValueExplorer', 'DiffExplorer', 'ExplorationError',
           'deep_comp', 'feq_comp', 'deep_feq', 'is_visit_primitive',
           'NEType', 'NotEqual', 'DiffersAtIndex', 'DiffersAtKey',
           'DiffersAtAttribute',
           'DifferentLength', 'DifferentTypes', 'SetDifferences', 
           'KeyDifferences')

#-------------------------------------------------------------------------------
