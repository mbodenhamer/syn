from .base import Type

#-------------------------------------------------------------------------------
# None


class NONE(Type):
    type = type(None)

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

    def _visit(self, k, **kwargs):
        return None

    def _visit_len(self, **kwargs):
        return 1


#-------------------------------------------------------------------------------
# __all__

__all__ = ('NONE',)

#-------------------------------------------------------------------------------
