import collections
from syn.five import unicode, xrange, izip
from syn.base_utils import REPL, repl_command, DefaultList, sgn, AttrDict
from syn.base_utils.rand import PRIMITIVE_TYPES

CONTAINERS = (collections.Mapping, collections.Sequence, set, frozenset)

#-------------------------------------------------------------------------------
# NEType


class NEType(object):
    def __init__(self, A, B):
        self.A = A
        self.B = B

    def __call__(self):
        self.explorer()()

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

    def explorer(self):
        xA = ValueExplorer(self.A, index=self.index)
        xB = ValueExplorer(self.B, index=self.index)
        return DiffExplorer(xA, xB)

    def message(self):
        iA = self.A[self.index]
        iB = self.B[self.index]
        return 'Sequences differ at index {}: {} != {}'.format(index, iA, iB)


#-----------------------------------------------------------


class DiffersAtKey(NEType):
    def __init__(self, A, B, key):
        super(DiffersAtKey, self).__init__(A, B)
        self.key = key

    def explorer(self):
        xA = ValueExplorer(self.A, key=self.key)
        xB = ValueExplorer(self.B, key=self.key)
        return DiffExplorer(xA, xB)

    def message(self):
        iA = self.A[self.key]
        iB = self.B[self.key]
        return 'Mappings differ at key {}: {} != {}'.format(key, iA, iB)


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
    pass


#-----------------------------------------------------------


class KeyDifferences(NEType):
    pass


#-------------------------------------------------------------------------------
# ExplorationError


class ExplorationError(Exception):
    pass


#-------------------------------------------------------------------------------
# ValueExplorer


class ValueExplorer(REPL):
    commands = dict(REPL.commands)
    command_help = dict(REPL.command_help)

    def __init__(self, value, index=None, key=None, prompt='(ValEx) ',
                 step=1):
        super(ValueExplorer, self).__init__(prompt)
        self.initial_value = value
        self.initial_index = index
        self.initial_key = key
        self.initial_step_value = step
        self._initialize(value, index, key, prompt, step)

    def _initialize(self, value, index, key, prompt, step):
        self.value = value
        self.index = index if index is not None else 0
        self.key = key
        self.step_value = step

        self.stack = DefaultList(None)
        self.stack_index = 0
        self.current_value = None
        self.at_end = False
        self._at_bottom_level()
        self._prime()

    def _at_bottom_level(self):
        if isinstance(self.value, CONTAINERS):
            self.at_bottom_level = False
        self.at_bottom_level = isinstance(self.value, tuple(PRIMITIVE_TYPES))

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
            else:
                self.step()

    def _pop(self):
        self.stack_index -= 1
        frame = self.stack.pop()
        self.value = frame['value']
        self.current_value = frame['current_value']
        self.index = frame['index']
        self.key = frame['key']
        self.at_end = frame['at_end']
        self.iter = frame['iter']
        self._at_bottom_level()

    def _push(self):
        frame = dict(value=self.value,
                     current_value=self.current_value,
                     index=self.index,
                     key=self.key,
                     iter=self.iter,
                     at_end=self.at_end)
        self.stack_index += 1
        self.stack.append(frame)

        self.value = self.current_value
        self.current_value = None
        self.index = 0
        self.key = None
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
            if isinstance(self.value, collections.Mapping):
                self.key = value[0]
                self.current_value = value[1]
            else:
                self.current_value = value
            self.index = index
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
                         self.initial_key, self.prompt, self.initial_step_value)

    def depth_first(self):
        vars = AttrDict(going_up=False,
                        going_forward=False)
        def step():
            try:
                self.step()
            except ExplorationError:
                if self.stack_index > 0:
                    self.up()
                    vars.going_up = True

        while True:
            if self.at_end and self.stack_index == 0:
                break

            if not vars.going_up and not vars.going_forward:
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
            
    @repl_command('l', 'display')
    def command_display(self):
        print(self.display())

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
    def __init__(self, A, B):
        if not isinstance(A, ValueExplorer):
            A = ValueExplorer(A)
        if not isinstance(B, ValueExplorer):
            B = ValueExplorer(B)

        self.A = A
        self.B = B

    def depth_first(self):
        for a, b in izip(self.A.depth_first(), self.B.depth_first()):
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


#-------------------------------------------------------------------------------
# Value (DEPRECATED)


class Value(object):
    def __init__(self, value):
        self.value = value

    def __call__(self):
        return self.value

    def __eq__(self, other):
        if not isinstance(other, Value):
            return False
        return self.value == other.value

    def __ne__(self, other):
        return not (self == other)


#-------------------------------------------------------------------------------
# FindNE (DEPRECATED)


class FindNE(REPL):
    @repl_command('b', 'go back')
    def go_back(self, step=1):
        pass

    @repl_command('f', 'go forward')
    def go_forward(self, step=1):
        pass


#-------------------------------------------------------------------------------
# __all__

__all__ = ('ValueExplorer', 'DiffExplorer', 'ExplorationError',
           'Value', 'FindNE')

#-------------------------------------------------------------------------------
