from syn.base_utils import this_module
from .base import Type, SER_KEYS

NoneType = type(None)

#-------------------------------------------------------------------------------
# None


class NONE(Type):
    type = NoneType

    @classmethod
    def deserialize(cls, dct, **kwargs):
        if dct is None:
            return
        return type(None)

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return None

    def estr(self, **kwargs):
        return 'None'

    def _find_ne(self, other, func, **kwargs):
        pass

    @classmethod
    def _generate(cls, **kwargs):
        return None

    @classmethod
    def serialize_type(cls, typ, **kwargs):
        dct = {SER_KEYS.name: 'NoneType',
               SER_KEYS.mod: this_module().__name__,
               SER_KEYS.is_type: True}
        return dct

    def _visit(self, k, **kwargs):
        return None

    def _visit_len(self, **kwargs):
        return 1


#-------------------------------------------------------------------------------
# __all__

__all__ = ('NONE',)

#-------------------------------------------------------------------------------
