from six import PY2, PY3
from syn.base_utils import rand_str, rand_unicode
from .base import Type, SER_KEYS

#-------------------------------------------------------------------------------
# String


class String(Type):
    type = str

    @classmethod
    def _generate(cls, **kwargs):
        return rand_str(**kwargs)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [self.obj]


#-------------------------------------------------------------------------------
# Unicode


class Unicode(String):
    if PY2:
        type = unicode
    else:
        type = None

    @classmethod
    def _generate(cls, **kwargs):
        return rand_unicode(**kwargs)


#-------------------------------------------------------------------------------
# Bytes


class Bytes(Type):
    if PY3:
        type = bytes

    @classmethod
    def _generate(cls, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        s = rand_str(**kwargs)
        return bytes(s.encode(encoding))

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = list(self.obj)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('String', 'Unicode', 'Bytes')

#-------------------------------------------------------------------------------
