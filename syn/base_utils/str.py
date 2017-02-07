import re
from functools import partial
from syn.five import STR, PY2, unicode, unichr
from .py import get_typename, hasmethod

#-------------------------------------------------------------------------------
# String-Quoting Utils

QUOTES_PATTERN = re.compile('^(\'\'\'|"""|\'|")')

def quote_string(obj):
    ret_type = type(obj)
    quotes = ["'", '"', "'''", '"""']
    quotes = [ret_type(q) for q in quotes]

    for quote in quotes:
        if quote not in obj:
            ret = quote + obj + quote
            return ret

    q = quotes[0]
    ret = obj.replace(q, ret_type("\'"))
    ret = q + ret + q
    return ret

def outer_quotes(string):
    m = re.match(QUOTES_PATTERN, string)
    if m:
        ret = m.groups()[0]
        if string.endswith(ret):
            return ret
    raise ValueError('String is not quoted')

def break_quoted_string(string, pattern, repl=None):
    if repl is None:
        repl = pattern

    if pattern not in string:
        return string

    quotes = outer_quotes(string)
    parts = string.split(pattern)

    def fix(s):
        ret = s
        if not ret.startswith(quotes):
            ret = quotes + ret
        if not ret.endswith(quotes):
            ret = ret + quotes
        return ret

    for k, part in enumerate(parts):
        parts[k] = fix(part)

    return repl.join(parts)

def break_around_line_breaks(string):
    lf = '\n'
    cr = '\r'
    crlf = '\r\n'

    ret = string
    ret = break_quoted_string(ret, crlf, lf)
    ret = break_quoted_string(ret, cr, lf)
    ret = break_quoted_string(ret, lf, lf)
    return ret

def escape_line_breaks(string):
    ret = string.replace('\r', '\\r')
    ret = ret.replace('\n', '\\n')
    return ret

def escape_null(string):
    ret = string.replace('\x00', '\\x00')
    return ret

def escape_for_eval(string):
    ret = string.replace('\\', '\\\\')
    ret = escape_line_breaks(ret)
    ret = escape_null(ret)
    return ret

#-------------------------------------------------------------------------------
# String Creation

def chrs(lst):
    return ''.join(chr(c) for c in lst)

#-------------------------------------------------------------------------------
# Unicode issues

def safe_chr(x):
    if PY2 and x > 255:
        return unichr(x)
    return chr(x)

def safe_str(x, encoding='utf-8'):
    try:
        return str(x)
    except UnicodeEncodeError:
        return x.encode(encoding)

def safe_unicode(x):
    try:
        return unicode(x)
    except UnicodeDecodeError:
        return u''.join(unichr(ord(c)) for c in x)

def safe_print(x, encoding='utf-8'):
    try:
        print(x)
    except UnicodeEncodeError:
        print(x.encode(encoding))

#-------------------------------------------------------------------------------
# istr

#-----------------------------------------------------------
# _istr_sequence

def _istr_sequence(seq, ret, pretty, indent):
    base = ','
    if pretty:
        indent += len(ret)
        base += '\n' + ' ' * indent
    else:
        base += ' '

    strs = [istr(val, pretty, indent) for val in seq]
    ret += base.join(strs)
    return ret

#-----------------------------------------------------------
# _istr_mapping

def _istr_mapping(dct, ret, pretty, indent):
    base = ','
    if pretty:
        indent += len(ret)
        base += '\n' + ' ' * indent
    else:
        base += ' '

    strs = []
    for key, val in dct.items():
        start = '{}: '.format(istr(key, pretty, indent))
        val_indent = indent + len(start)
        tmp = start + istr(val, pretty, val_indent)
        strs.append(tmp)

    ret += base.join(strs)
    return ret

#-----------------------------------------------------------
# istr_list

def _istr_list(lst, pretty, indent):
    if type(lst) is not list:
        ret = '{}(['.format(get_typename(lst))
        end = '])'
    else:
        ret = '['
        end = ']'

    ret = _istr_sequence(lst, ret, pretty, indent) + end
    return ret

#-----------------------------------------------------------
# istr_dict

def _istr_dict(dct, pretty, indent):
    if type(dct) is not dict:
        ret = '{}({{'.format(get_typename(dct))
        end = '})'
    else:
        ret = '{'
        end = '}'

    ret = _istr_mapping(dct, ret, pretty, indent) + end
    return ret

#-----------------------------------------------------------
# istr_set

def _istr_set(obj, pretty, indent):
    if type(obj) is not set:
        ret = '{}(['.format(get_typename(obj))
        end = '])'
    else:
        if len(obj) == 1:
            ret = 'set(['
            end = '])'
        else:
            ret = '{'
            end = '}'

    ret = _istr_sequence(obj, ret, pretty, indent) + end
    return ret

#-----------------------------------------------------------
# istr_tuple

def _istr_tuple(tup, pretty, indent):
    if type(tup) is not tuple:
        ret = '{}(['.format(get_typename(tup))
        end = '])'
    else:
        ret = '('
        end = ')'

    ret = _istr_sequence(tup, ret, pretty, indent) + end
    return ret

#-----------------------------------------------------------
# istr_str

def _istr_str(s, pretty, indent):
    ret = quote_string(s)
    if PY2:
        if isinstance(s, unicode):
            ret = 'u' + ret
    return ret

#-----------------------------------------------------------
# istr_type

def _istr_type(obj, pretty, indent):
    return get_typename(obj)

#-----------------------------------------------------------
# istr_object

def _istr_object(obj, pretty, indent):
    if hasmethod(obj, 'istr'):
        return obj.istr(pretty, indent)
    return str(obj)

#-----------------------------------------------------------
# istr

def istr(obj, pretty=False, indent=0):
    if isinstance(obj, list):
        return _istr_list(obj, pretty, indent)

    if isinstance(obj, dict):
        return _istr_dict(obj, pretty, indent)

    if isinstance(obj, set):
        return _istr_set(obj, pretty, indent)

    if isinstance(obj, tuple):
        return _istr_tuple(obj, pretty, indent)

    if isinstance(obj, STR):
        return _istr_str(obj, pretty, indent)

    if isinstance(obj, type):
        return _istr_type(obj, pretty, indent)

    return _istr_object(obj, pretty, indent)
        
#-------------------------------------------------------------------------------
# pretty

pretty = partial(istr, pretty=True)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('quote_string', 'outer_quotes', 'break_quoted_string',
           'break_around_line_breaks', 
           'escape_line_breaks', 'escape_null', 'escape_for_eval',
           'chrs',
           'safe_chr', 'safe_str', 'safe_unicode', 'safe_print',
           'istr', 'pretty')

#-------------------------------------------------------------------------------
