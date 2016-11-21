import sys
from six import PY2, PY3
from syn.five import STR
from syn.base_utils import rand_str, rand_unicode, get_typename, quote_string, \
    safe_chr, escape_for_eval
from .base import Type, SER_KEYS
from .ne import Value

#-------------------------------------------------------------------------------
# Utilities

# TODO: implement a size-limited cache for this sort of thing
_STRING_ENUMVALS = {}

def string_enumval(x, **kwargs):
    top_level = kwargs.get('top_level', True)
    if top_level:
        if x == 0:
            return ''

        kwargs['top_level'] = False
        return string_enumval(x - 1, **kwargs)

    if x+1 in _STRING_ENUMVALS:
        return _STRING_ENUMVALS[x+1]

    min_char = kwargs.get('min_char', ' ')
    max_char = kwargs.get('max_char', '~')

    if not isinstance(min_char, int):
        min_char = ord(min_char)
    if not isinstance(max_char, int):
        max_char = ord(max_char)

    N = max_char - min_char + 1

    if x >= N:
        ret = string_enumval(x // N - 1, **kwargs) + string_enumval(x % N, **kwargs)
    else:
        ret = safe_chr(x + min_char)

    _STRING_ENUMVALS[x+1] = ret
    return ret

#-------------------------------------------------------------------------------
# String


class String(Type):
    type = str

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        return string_enumval(x, **kwargs)

    def _find_ne(self, other, **kwargs):
        # TODO: replace with FindNE objects

        if self.obj != other:
            # TODO: eliminate this case: check at which index they
            # become inequal even if they are of different length
            if len(self.obj) != len(other):
                return Value('length-{} string != length-{} string'
                             .format(len(self.obj), len(other)))

            for k, item in enumerate(self.obj):
                if item != other[k]:
                    return Value('strings differ at index {}'
                                 .format(k))

    def _hashable(self, **kwargs):
        return self

    @classmethod
    def _generate(cls, **kwargs):
        return rand_str(**kwargs)

    def _serialize(self, dct, **kwargs):
        dct[SER_KEYS.args] = [self.obj]

    def _visit(self, k, **kwargs):
        return self.obj[k]

    def _visit_len(self, **kwargs):
        return len(self.obj)


#-------------------------------------------------------------------------------
# Unicode


class Unicode(String):
    if PY2:
        type = unicode
    else:
        type = None

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        kwargs['max_char'] = kwargs.get('max_char', sys.maxunicode)
        s = super(Unicode, cls)._enumeration_value(x, **kwargs)
        return unicode(s)

    def estr(self, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        objstr = escape_for_eval(quote_string(self.obj.encode(encoding)))
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


class Bytes(String):
    if PY3:
        type = bytes
    else:
        type = None

    def estr(self, **kwargs):
        encoding = kwargs.get('encoding', 'utf-8')
        objstr = str(self.obj)
        return objstr

    @classmethod
    def _enumeration_value(cls, x, **kwargs):
        s = super(Bytes, cls)._enumeration_value(x, **kwargs)
        encoding = kwargs.get('encoding', 'utf-8')
        return bytes(s.encode(encoding))

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
