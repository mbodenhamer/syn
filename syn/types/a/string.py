from six import PY2, PY3
from syn.base_utils import rand_str, rand_unicode, get_typename, quote_string
from .base import Type, SER_KEYS
from .ne import Value

#-------------------------------------------------------------------------------
# String


class String(Type):
    type = str

    def _find_ne(self, other, **kwargs):
        if self.obj != other:
            if len(self.obj) != len(self.other):
                return Value('length-{} string != length-{} string'
                             .format(len(self.obj), len(other)))

            for k, item in enumerate(self.obj):
                if item != other[k]:
                    return Value('strings differ at index {}'
                                 .format(k))

    @classmethod
    def _generate(cls, **kwargs):
        return rand_str(**kwargs)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [self.obj]

    def _visit(self, k, **kwargs):
        yield self.obj[k]

    def _visit_len(self, **kwargs):
        return len(self.obj)


#-------------------------------------------------------------------------------
# Unicode


class Unicode(String):
    if PY2:
        type = unicode
    else:
        type = None

    def estr(self, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        objstr = quote_string(self.obj.encode(encoding))
        objstr += '.decode("{}")'.format(encoding)
        return '{}({})'.format(get_typename(self.obj), objstr)

    def rstr(self, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        return self.obj.encode(encoding)

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
        dct[SER_KEYS.args] = [list(self.obj)]


#-------------------------------------------------------------------------------
# __all__

__all__ = ('String', 'Unicode', 'Bytes')

#-------------------------------------------------------------------------------
