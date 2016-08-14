from weakref import WeakSet
from syn.five import STR, strf
from collections import Iterable
from random import randrange, choice
from syn.base_utils import hasmethod, message, nearest_base, get_typename, \
    istr, rand_primitive, collection_equivalent

#-------------------------------------------------------------------------------
# Type Registry

GENERABLE_TYPE_REGISTRY = WeakSet()

#-------------------------------------------------------------------------------
# Base Class


class Type(object):
    '''A representation for various possible types syn supports.'''
    __slots__ = ('__weakref__',)
    register_generable = False

    def __init__(self):
        if self.register_generable:
            GENERABLE_TYPE_REGISTRY.add(self)

    def __eq__(self, other):
        return type(self) is type(other)

    def __ne__(self, other):
        return not self == other

    def __hash__(self):
        return hash(id(self))

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

    def display(self):
        '''Returns a quasi-intuitive string representation of the type.'''
        raise NotImplementedError

    def generate(self, **kwargs):
        '''Returns a value for this type.'''
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

    def rst(self):
        '''Returns a string representation of the type for RST documentation.'''
        return self.display()

    def validate(self, value):
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Any Type


class AnyType(Type):
    def check(self, value):
        pass

    def coerce(self, value):
        return value

    def display(self):
        return 'any'

    def generate(self, **kwargs):
        max_enum = kwargs.get('max_enum', 20)
        types = kwargs.get('types', GENERABLE_TYPE_REGISTRY)
        N = randrange(min(len(types), max_enum))

        for k, typ in enumerate(types):
            if k == N:
                try:
                    return typ.generate(**kwargs)
                except:
                    return rand_primitive()

    def validate(self, value):
        pass


#-------------------------------------------------------------------------------
# Type Type


class TypeType(Type):
    __slots__ = ('type', 'call_coerce', 'call_validate')
    register_generable = True

    def __init__(self, typ):
        super(TypeType, self).__init__()
        self.type = typ
        self.call_coerce = hasmethod(self.type, 'coerce')
        self.call_validate = hasmethod(self.type, 'validate')

    def __eq__(self, other):
        if super(TypeType, self).__eq__(other):
            if self.type == other.type:
                if self.call_coerce == other.call_coerce:
                    if self.call_validate == other.call_validate:
                        return True
        return False

    def __hash__(self):
        return hash(id(self))

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

    def display(self):
        return get_typename(self.type)

    def generate(self, **kwargs):
        from .registry import TYPE_REGISTRY

        if hasmethod(self.type, '_generate'):
            return self.type._generate(**kwargs)
        elif self.type in TYPE_REGISTRY:
            return TYPE_REGISTRY[self.type].generate(**kwargs)
        raise TypeError('Unable to generate value for type: {}'
                        .format(self.type))

    def rst(self):
        return '*' +  self.display() + '*'

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
    register_generable = True

    def __init__(self, values):
        super(ValuesType, self).__init__()
        self.values = values

        self.indexed_values = values
        if not hasattr(values, '__getitem__'):
            self.indexed_values = list(values)

    def __eq__(self, other):
        if super(ValuesType, self).__eq__(other):
            if collection_equivalent(self.indexed_values, other.indexed_values):
                return True
        return False

    def __hash__(self):
        return hash(id(self))

    def check(self, value):
        if value not in self.values:
            raise TypeError('Invalid value: {}'.format(value))

    def coerce(self, value):
        try:
            self.check(value)
        except TypeError as e:
            raise TypeError('Cannot coerce {}: {}'.format(value, message(e)))
        return value

    def display(self):
        return istr(list(self.values))

    def generate(self, **kwargs):
        return choice(self.indexed_values)

    def validate(self, value):
        self.check(value)


#-------------------------------------------------------------------------------
# MultiType


class MultiType(Type):
    '''A tuple of type specifiers, any of which may be valid.
    '''
    __slots__ = ('types', 'typestr', 'typelist', 'typemap', 'is_typelist')
    register_generable = True

    def __init__(self, types):
        super(MultiType, self).__init__()
        self.is_typelist = False
        if all(isinstance(typ, type) for typ in types):
            self.is_typelist = True
            self.typelist = types
            
        self.typestr = ', '.join(map(strf, types))
        self.types = [Type.dispatch(typ) for typ in types]
        self.typemap = dict(zip(types, self.types))

    def __eq__(self, other):
        if super(MultiType, self).__eq__(other):
            if self.types == other.types:
                return True
        return False

    def __hash__(self):
        return hash(id(self))

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

    def display(self):
        strs = [typ.display() for typ in self.types]
        return ' | '.join(strs)

    def generate(self, **kwargs):
        typ = choice(self.types)
        return typ.generate(**kwargs)

    def rst(self):
        strs = [typ.rst() for typ in self.types]
        return ' | '.join(strs)

    def validate(self, value):
        typ = self.check(value)
        typ.validate(value)
        

#-------------------------------------------------------------------------------
# Set


class Set(Type):
    '''For explicitly wrapping a SetNode as a type (since automatic
    dispatching cannot be implemented at this level).
    '''
    register_generable = True

    def __init__(self, set):
        super(Set, self).__init__()
        self.set = set
        self.set.validate()

    def __eq__(self, other):
        if super(Set, self).__eq__(other):
            if self.set == other.set:
                return True
        return False

    def __hash__(self):
        return hash(id(self))

    def check(self, value):
        if not self.set.hasmember(value):
            raise TypeError('Set does not contain value: {}'.format(value))

    def display(self):
        return '<Set>'

    def generate(self, **kwargs):
        return self.set.sample(**kwargs)
    
    def validate(self, value):
        self.check(value)


#-------------------------------------------------------------------------------
# Schema


class Schema(Type):
    '''For explicitly wrapping a Schema as a type (since automatic
    dispatching cannot be implemented at this level).
    '''
    register_generable = True

    def __init__(self, schema):
        super(Schema, self).__init__()
        self.schema = schema

    def __eq__(self, other):
        if super(Schema, self).__eq__(other):
            if self.schema == other.schema:
                return True
        return False

    def __hash__(self):
        return hash(id(self))

    def check(self, value):
        if not self.schema.match(value):
            raise TypeError('Schema does not match: {}'.format(value))

    def display(self):
        return '<Schema>'

    def generate(self, **kwargs):
        return self.schema.sample(**kwargs)
    
    def validate(self, value):
        self.check(value)


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
           'Set', 'Schema',
           'TypeExtension')

#-------------------------------------------------------------------------------
