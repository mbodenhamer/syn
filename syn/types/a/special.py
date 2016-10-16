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

    @classmethod
    def _generate(cls, **kwargs):
        return None


#-------------------------------------------------------------------------------
# __all__

__all__ = ('NONE',)

#-------------------------------------------------------------------------------
