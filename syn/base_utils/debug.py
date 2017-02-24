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
        switch[event](frame)

    def c_call(self, frame):
        raise NotImplementedError

    def c_exception(self, frame):
        raise NotImplementedError

    def c_return(self, frame):
        raise NotImplementedError

    def call(self, frame):
        raise NotImplementedError

    def exception(self, frame):
        raise NotImplementedError

    def line(self, frame):
        raise NotImplementedError

    def return_(self, frame):
        raise NotImplementedError


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Trace',)

#-------------------------------------------------------------------------------
