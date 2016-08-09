import six

STR = six.string_types

if six.PY2:
    strf = unicode
    unicode = unicode
    unichr = unichr
else:
    strf = str
    unicode = str
    unichr = chr

#-------------------------------------------------------------------------------
# __all__

__all__ = ('STR', 'strf', 'unicode', 'unichr')

#-------------------------------------------------------------------------------
