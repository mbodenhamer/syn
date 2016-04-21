import yaml
from six.moves import cStringIO
from syn.type import Type

#-------------------------------------------------------------------------------
# Base mixin


class ConfMixin(object):
    @classmethod
    def from_file(cls, fil):
        raise NotImplementedError

    @classmethod
    def from_string(cls, s):
        return cls.from_file(cStringIO(s))


#-------------------------------------------------------------------------------
# Dict-based configuration


class DictMixin(ConfMixin):
    @classmethod
    def from_dict(cls, dct):
        t = Type.dispatch(cls)
        return t.coerce(dct)


#-------------------------------------------------------------------------------
# YAML


class YAMLMixin(DictMixin):
    @classmethod
    def from_file(cls, fil):
        return cls.from_dict(yaml.load(fil))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('YAMLMixin',)

#-------------------------------------------------------------------------------
