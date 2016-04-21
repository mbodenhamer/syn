from syn.five import STR, strf
from collections import Iterable
from syn.base_utils import hasmethod, message, nearest_base

#-------------------------------------------------------------------------------
# Base Class


class Type(object):
    '''A representation for various possible types syn supports.'''
    __slots__ = ()

    def check(self, value):
        raise NotImplementedError

    @classmethod
    def dispatch(cls, obj):
        if isinstance(obj, Type):
            return obj

        if obj is None:
            return AnyType()

        if isinstance(obj, type):
            if issubclass(obj, TypeExtension):
                return obj()
            return TypeType(obj)

        if isinstance(obj, tuple):
            # Treat a singleton tuple as its element
            if len(obj) == 1:
                return cls.dispatch(obj[0])
            return MultiType(obj)

        # Exclude bytes b/c it is more closely related to string than list
        if isinstance(obj, Iterable) and not isinstance(obj, STR + (bytes,)):
            return ValuesType(obj)

        raise TypeError('Unable to dispatch appropriate type represetation'
                         ' for {}'.format(obj))

    def coerce(self, value):
        raise NotImplementedError

    def query(self, value):
        try:
            self.check(value)
            return True
        except TypeError:
            return False

    def query_exception(self, value):
        try:
            self.check(value)
            return True, None
        except TypeError as e:
            return False, e

    def validate(self, value):
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Any Type


class AnyType(Type):
    def check(self, value):
        pass

    def coerce(self, value):
        return value

    def validate(self, value):
        pass


#-------------------------------------------------------------------------------
# Type Type


class TypeType(Type):
    __slots__ = ('type', 'call_coerce', 'call_validate')

    def __init__(self, typ):
        self.type = typ
        self.call_coerce = hasmethod(self.type, 'coerce')
        self.call_validate = hasmethod(self.type, 'validate')

    def check(self, value):
        if not isinstance(value, self.type):
            raise TypeError('Expected value of type {}; got: {}'
                            .format(self.type, value))

    def coerce(self, value):
        if self.query(value):
            return value

        try:
            if self.call_coerce:
                return self.type.coerce(value)
            return self.type(value)
        except Exception as e:
            raise TypeError('Cannot coerce {} to type {}: {}'
                            .format(value, self.type, message(e)))

    def validate(self, value):
        self.check(value)

        if self.call_validate:
            value.validate()


#-------------------------------------------------------------------------------
# Values Type


class ValuesType(Type):
    '''A set (or list) of values, any of which is valid.

    Think of this is a denotational definition of the type.
    '''
    __slots__ = ('values', 'indexed_values')

    def __init__(self, values):
        self.values = values

        self.indexed_values = values
        if not hasattr(values, '__getitem__'):
            self.indexed_values = list(values)

    def check(self, value):
        if value not in self.values:
            raise TypeError('Invalid value: {}'.format(value))

    def coerce(self, value):
        try:
            self.check(value)
        except TypeError as e:
            raise TypeError('Cannot coerce {}: {}'.format(value, message(e)))
        return value

    def validate(self, value):
        self.check(value)


#-------------------------------------------------------------------------------
# MultiType


class MultiType(Type):
    '''A tuple of type specifiers, any of which may be valid.
    '''
    __slots__ = ('types', 'typestr', 'typelist', 'typemap', 'is_typelist')

    def __init__(self, types):
        self.is_typelist = False
        if all(isinstance(typ, type) for typ in types):
            self.is_typelist = True
            self.typelist = types
            
        self.typestr = ', '.join(map(strf, types))
        self.types = [Type.dispatch(typ) for typ in types]
        self.typemap = dict(zip(types, self.types))

    def check(self, value):
        if self.is_typelist:
            if isinstance(value, self.typelist):
                return self.typemap[nearest_base(type(value), self.typelist)]
        
        else:
            for typ in self.types:
                try:
                    typ.check(value)
                    return typ
                except TypeError:
                    pass
        
        raise TypeError("Value '{}' is not any valid type: {}"
                        .format(value, self.typestr))

    def coerce(self, value):
        for typ in self.types:
            try:
                return typ.coerce(value)
            except TypeError:
                pass

        raise TypeError('Cannot coerce {} to any valid type: {}'
                        .format(value, self.typestr))

    def validate(self, value):
        typ = self.check(value)
        typ.validate(value)
        

#-------------------------------------------------------------------------------
# TypeExtension


class TypeExtension(Type):
    '''For extending the type system.
    '''

    def validate(self, value):
        self.check(value)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Type', 'AnyType', 'TypeType', 'ValuesType', 'MultiType', 
           'TypeExtension')

#-------------------------------------------------------------------------------
