import collections
from syn.five import unicode, xrange
from syn.base_utils import REPL, repl_command, DefaultList, sgn
from syn.base_utils.rand import PRIMITIVE_TYPES

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
        self.value = value
        self.index = index if index is not None else 0
        self.key = key
        self.step_value = step

        self.stack = DefaultList(None)
        self.stack_index = 0
        self.current_value = None
        self._at_bottom_level()
        self._prime()
        self.step()

    def _at_bottom_level(self):
        if isinstance(self.value, (collections.Mapping, collections.Sequence)):
            self.at_bottom_level = False
        self.at_bottom_level = isinstance(self.value, tuple(PRIMITIVE_TYPES))

    def _prime(self):
        from .base import visit
        self.iter = visit(self.value, k=self.index, step=self.step_value)

    def _pop(self, delta=-1, save=True):
        if save:
            self._push(delta=0, save_only=True)

        self.stack_index += delta
        frame = self.stack[self.stack_index]
        self.value = frame['value']
        self.current_value = frame['current_value']
        self.index = frame['index']
        self.key = frame['key']
        self._at_bottom_level()
        self._prime()

    def _push(self, delta=1, save_only=False):
        frame = dict(value=self.value,
                     current_value=self.current_value,
                     index=self.index,
                     key=self.key)
        self.stack[self.stack_index] = frame
        self.stack_index += delta

        if save_only:
            return

        if self.stack_index < len(self.stack):
            self._pop(delta=0, save=False)
        else:
            self.value = self.current_value
            self.index = 0
            self._at_bottom_level()
            self._prime()
            self.step()

    def display(self):
        return unicode(self.current_value)

    def step(self, step=None):
        step = int(step) if step is not None else self.step_value
        if step != self.step_value:
            if sgn(step) != sgn(self.step_value):
                if step < 0:
                    self.index -= 1
                elif step > 0:
                    self.index += 1

            self.step_value = step
            self._prime()

        try:
            self.current_value = next(self.iter)
            self.index += self.step_value
        except StopIteration:
            raise ExplorationError('At last value')
        
    def down(self):
        if self.at_bottom_level:
            raise ExplorationError('At bottom level')
        self._push()

    def up(self):
        if self.stack_index == 0:
            raise ExplorationError('At top level')
        self._pop()

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
    pass


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

__all__ = ('ValueExplorer', 'ExplorationError',
           'Value', 'FindNE')

#-------------------------------------------------------------------------------
