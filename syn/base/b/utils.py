from .base import Base
from .meta import Attr

#-------------------------------------------------------------------------------
# Utilities

Num = (int, float)

#-------------------------------------------------------------------------------
# Counter


class Counter(Base):
    _attrs = dict(value = Attr(Num, default = -1, doc="The current count"),
                  # TODO: replace with List(This) when that is available
                  resets = Attr(list, init=lambda s: list(),
                                doc="A list of counters to reset when this "\
                                "counter is reset"),
                  initial_value = Attr(Num, init=lambda self: self.value, 
                                       doc="The initial "\
                                       "value to which the counter is reset"),
                  threshold = Attr(Num, optional=True, doc="Threshold at which"\
                                   " to reset the counter"),
                  step = Attr(Num, default = 1, 
                              doc="Amount by which to increment the counter"),
                )
    _opts = dict(optional_none = True,
                 init_validate = True)

    def __call__(self, step=None):
        if step is None:
            step = self.step

        self.value += step
        ret = self.value

        for counter in self.resets:
            counter.reset()

        if self.threshold is not None:
            if self.value >= self.threshold:
                self.reset()
        
        return ret

    def peek(self):
        return self.value

    def reset(self):
        self.value = self.initial_value

    def validate(self):
        super(Counter, self).validate()
        
        if self.threshold is not None:
            if self.value >= self.threshold:
                raise ValueError("value cannot be greater than threshold")


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Counter',)

#-------------------------------------------------------------------------------
