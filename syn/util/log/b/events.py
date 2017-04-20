from .base import Event, Attr
from syn.five import STR
from syn.base_utils import get_typename

#-------------------------------------------------------------------------------
# StringEvent


class StringEvent(Event):
    _attrs = dict(s = Attr(STR))

    def plaintext(self, **kwargs):
        indent_level = kwargs.get('indent_level', 0)
        indent = kwargs.get('indent', ' ')
        pre = indent * indent_level

        ret = pre + get_typename(self) + '(' + self.s
        if self._children:
            kwargs['indent_level'] = indent_level + 1
            ret += '\n' + super(StringEvent, self).plaintext(**kwargs)
        ret += ')'
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('StringEvent',)

#-------------------------------------------------------------------------------
