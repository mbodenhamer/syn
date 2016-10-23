from syn.base import Base, ListWrapper, Attr
from syn.schema.b.sequence import ZeroOrMore


#-------------------------------------------------------------------------------
# ConfDict


# Use DictMixin for from_dict()

class ConfDict(Base):
    pass


#-------------------------------------------------------------------------------
# ConfList


class ConfList(ListWrapper):
    schema = ZeroOrMore(None) # TODO: replace with an AnyType set


#-------------------------------------------------------------------------------
# Conf


class Conf(ConfDict):
    _attrs = dict(_env = Attr(dict),
                  vars = Attr(ConfDict))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('ConfDict', 'ConfList', 'Conf')

#-------------------------------------------------------------------------------
