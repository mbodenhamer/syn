import six.moves.builtins as builtins
from six import PY2, PY3
from .base import Type

#-------------------------------------------------------------------------------
# BaseString


class BaseString(Type):
    if PY2:
        type = builtins.basestring


#-------------------------------------------------------------------------------
# String


class String(BaseString):
    type = str


#-------------------------------------------------------------------------------
# Unicode


class Unicode(BaseString):
    if PY2:
        type = unicode


#-------------------------------------------------------------------------------
# Bytes


class Bytes(BaseString):
    if PY3:
        type = bytes


#-------------------------------------------------------------------------------
# __all__

__all__ = ('BaseString', 
           'String', 'Unicode', 'Bytes')

#-------------------------------------------------------------------------------
