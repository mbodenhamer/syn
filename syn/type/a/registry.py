'''An attempt at handling the various builtin Python types in a sane and unified way.
'''
import six
import collections
from syn.base_utils import rand_dispatch

#-------------------------------------------------------------------------------
# Registry

TYPE_REGISTRY = dict()

#-------------------------------------------------------------------------------
# Registrar Metaclass


class RegistrarMeta(type):
    def __init__(self, *args):
        super(RegistrarMeta, self).__init__(*args)
        if self.type is not None:
            TYPE_REGISTRY[self.type] = self


#-------------------------------------------------------------------------------
# Registrar


@six.add_metaclass(RegistrarMeta)
class Registrar(object):
    gen = None
    type = None
    real_type = None

    @classmethod
    def coerce(cls, obj, **kwargs):
        return cls.type(obj)

    @classmethod
    def generate(cls, **kwargs):
        if cls.gen is not None:
            return cls.gen
        if cls.real_type is not None:
            return rand_dispatch(cls.real_type, **kwargs)
        return rand_dispatch(cls.type, **kwargs)


#-------------------------------------------------------------------------------
# Numeric

class Bool(Registrar):
    type = bool

class Int(Registrar):
    type = int

class Float(Registrar):
    type = float

class Complex(Registrar):
    type = complex

if six.PY2:
    class Long(Registrar):
        type = long

#-------------------------------------------------------------------------------
# String

class Str(Registrar):
    type = str

if six.PY2:
    class Unicode(Registrar):
        type = unicode

if six.PY3:
    class Bytes(Registrar):
        type = bytes

#-------------------------------------------------------------------------------
# Sequence

class List(Registrar):
    type = list

class Tuple(Registrar):
    type = tuple

class Sequence(Registrar):
    type = collections.Sequence
    real_type = tuple

class MutableSequence(Registrar):
    type = collections.MutableSequence
    real_type = list

#-------------------------------------------------------------------------------
# Set

class Set(Registrar):
    type = set

class FrozenSet(Registrar):
    type = frozenset

#-------------------------------------------------------------------------------
# Mapping

class Dict(Registrar):
    type = dict

class Mapping(Registrar):
    type = collections.Mapping
    real_type = dict # TODO: find a better real_type

class MutableMapping(Registrar):
    type = collections.MutableMapping
    real_type = dict

#-------------------------------------------------------------------------------
# Iterable

class Generator(Registrar):
    gen = (x for x in range(1))
    type = type(gen)

#-------------------------------------------------------------------------------
# Callable

class Type(Registrar):
    gen = type
    type = gen

class Function(Registrar):
    type = type(lambda x: x)

    @classmethod
    def generate(cls, **kwargs):
        return lambda x: x

class Method(Registrar):
    gen = Function.__init__
    type = type(gen)

class BuiltinFunction(Registrar):
    gen = sum
    type = type(gen)

if six.PY2:
    class Old:
        pass

    class OldStyleClass(Registrar):
        gen = Old
        type = type(gen)

#-------------------------------------------------------------------------------
# Misc.

class Module(Registrar):
    gen = six
    type = type(gen)

class NONE(Registrar):
    type = type(None)

if six.PY2:
    class Instance(Registrar):
        gen = Old()
        type = type(gen)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('TYPE_REGISTRY',)

#-------------------------------------------------------------------------------
