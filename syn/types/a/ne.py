from syn.base_utils import REPL, repl_command

#-------------------------------------------------------------------------------
# Value


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
# FindNE


class FindNE(REPL):
    @repl_command('b', 'go back')
    def go_back(self, step=1):
        pass

    @repl_command('f', 'go forward')
    def go_forward(self, step=1):
        pass


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Value', 'FindNE')

#-------------------------------------------------------------------------------
