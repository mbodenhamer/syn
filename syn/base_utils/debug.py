import sys
from contextlib import contextmanager

#-------------------------------------------------------------------------------
# Trace


class Trace(object):
    def __call__(self, frame, event, arg):
        switch = dict(c_call = self.c_call,
                      c_exception = self.c_exception,
                      c_return = self.c_return,
                      call = self.call,
                      exception = self.exception,
                      line = self.line)
        switch['return'] = self.return_

        if event not in switch:
            raise RuntimeError('Invalid event: {}'.format(event))
        return switch[event](frame, arg)

    def c_call(self, frame, arg):
        return self

    def c_exception(self, frame, arg):
        return self

    def c_return(self, frame, arg):
        return self

    def call(self, frame, arg):
        return self

    def exception(self, frame, arg):
        return self

    def line(self, frame, arg):
        return self

    def return_(self, frame, arg):
        return self


#-------------------------------------------------------------------------------
# CallTrace


class CallTrace(Trace):
    def __init__(self, indent=0, tab=' '):
        self.indent = indent
        self.tab = tab

    def call(self, frame, arg):
        pre = self.tab * self.indent
        print(pre + frame.f_code.co_name)
        self.indent += 1
        return self

    def return_(self, frame, arg):
        self.indent -= 1
        return self


#-------------------------------------------------------------------------------
# Utilities

def call_trace(**kwargs):
    sys.settrace(CallTrace(**kwargs))

@contextmanager
def reset_trace():
    tr = sys.gettrace()
    try:
        yield
    finally:
        sys.settrace(tr) # pragma: no cover

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Trace', 'CallTrace',
           'call_trace', 'reset_trace')

#-------------------------------------------------------------------------------
