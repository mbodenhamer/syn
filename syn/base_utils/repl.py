import six
import shlex
from .py import message, get_typename
from syn.five import raw_input

#-------------------------------------------------------------------------------
# command decorator

class repl_command(object):
    def __init__(self, name, help=''):
        self.name = name
        self.help = help

    def __call__(self, f):
        f.command_name = self.name
        f.command_help = self.help
        return f

#-------------------------------------------------------------------------------
# REPLMeta


class REPLMeta(type):
    def __init__(self, clsname, bases, dct):
        super(REPLMeta, self).__init__(clsname, bases, dct)

        for name, item in dct.items():
            if callable(item):
                if hasattr(item, 'command_name'):
                    if isinstance(item.command_name, (list, tuple)):
                        names = item.command_name
                    else:
                        names = [item.command_name]

                    for name in names:
                        self.commands[name] = item
                        self.command_help[name] = item.command_help


#-------------------------------------------------------------------------------
# REPL


@six.add_metaclass(REPLMeta)
class REPL(object):
    commands = {}
    command_help = {}

    def __init__(self, prompt=''):
        self.prompt = prompt

    def __call__(self):
        self._loop()

    def _loop(self):
        self.quit = False
        while True:
            try:
                inpt = raw_input(self.prompt)
            except (EOFError, KeyboardInterrupt):
                break

            self._eval(inpt)
            if self.quit:
                break

    def _eval(self, inpt):
        inpts = shlex.split(inpt)
        command = inpts[0]
        args = inpts[1:]

        if command not in self.commands:
            print('Unrecognized command: {}'.format(command))
            return

        try:
            self.commands[command](self, *args)
        except Exception as e:
            print("Error in {}: ***{}***: {}".format(command, 
                                               get_typename(e), 
                                               message(e)))

    @repl_command(['h', '?'], 'display available commands')
    def print_commands(self, **kwargs):
        # TODO: use texttable here
        for command in sorted(self.commands.keys()):
            print(" {:15} {}".format(command, self.command_help[command]))

    @repl_command('e', 'eval the argument')
    def eval(self, expr):
        print(eval(expr))

    @repl_command('q', 'quit')
    def quit(self, *args, **kwargs):
        self.quit = True


#-------------------------------------------------------------------------------
# __all__

__all__ = ('REPL', 'repl_command')

#-------------------------------------------------------------------------------
