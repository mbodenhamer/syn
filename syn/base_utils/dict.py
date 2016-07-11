''' Various dict extensions.
'''
import collections
from functools import reduce

#-------------------------------------------------------------------------------
# Utilities

def is_assoc_list(lst):
    if not isinstance(lst, list):
        return False

    if not all(isinstance(val, tuple) for val in lst):
        return False

    if not all(len(val) == 2 for val in lst):
        return False

    return True

def dict_arg(*args, **kwargs):
    if len(args) == 1:
        if isinstance(args[0], dict):
            return args[0]
        elif is_assoc_list(args[0]):
            return args[0]
        else:
            raise TypeError('Invalid arguments')
    elif len(args) == 0:
        if kwargs:
            return kwargs
        return {}
    else:
        raise TypeError('expected at most 1 arguments, got {}'
                        .format(len(args)))

#-------------------------------------------------------------------------------
# AttrDict


class AttrDict(dict):
    '''A dict whose items can be accessed as attributes.
    '''
    __slots__ = ()

    def __getattr__(self, attr):
        if attr not in self:
            raise AttributeError("No attribute '{}' present".format(attr))
        return self[attr]

    def __setattr__(self, attr, val):
        self[attr] = val

    def __delattr__(self, attr):
        if attr not in self:
            raise AttributeError("No attribute '{}' present".format(attr))
        del self[attr]


#-------------------------------------------------------------------------------
# UpdateDict


class UpdateDict(dict):
    '''A dict with an extensible update() hook.
    '''

    def __init__(self, *args, **kwargs):
        super(UpdateDict, self).__init__(*args, **kwargs)
        self._update()

    def __setitem__(self, key, value):
        super(UpdateDict, self).__setitem__(key, value)
        self._update()

    def __delitem__(self, key):
        super(UpdateDict, self).__delitem__(key)
        self._update()

    def _update(self):
        raise NotImplementedError

    def update(self, *args, **kwargs):
        super(UpdateDict, self).update(*args, **kwargs)
        self._update()


#-------------------------------------------------------------------------------
# GroupDict


class GroupDict(AttrDict):
    '''An AttrDict whose items are treated as sets.
    '''

    def complement(self, *args):
        '''Returns the difference of the union of all values and the union of the values in *args.
        '''
        universe = self.union()
        to_diff = self.union(*args)
        return universe.difference(to_diff)

    def intersection(self, *args):
        '''Returns the intersection of the values whose keys are in *args.  If *args is blank, returns the intersection of all values.
        '''
        values = self.values()
        if args:
            values = [val for key,val in self.items() if key in args]
        return set(reduce(set.intersection, values))

    def union(self, *args):
        '''Returns the union of the values whose keys are in *args.  If *args is blank, returns the union of all values.
        '''
        values = self.values()
        if args:
            values = [val for key,val in self.items() if key in args]
        return set(reduce(set.union, values))

    def update(self, *args, **kwargs):
        other = dict(dict_arg(*args, **kwargs))

        for key, val in other.items():
            if key not in self:
                self[key] = val
            else:
                self[key].update(val)


SetDict = GroupDict # Alias

#-------------------------------------------------------------------------------
# ReflexiveDict


class ReflexiveDict(AttrDict):
    '''An AttrDict for which each key == the associated value.
    '''
    def __init__(self, *args, **kwargs):
        if args and not kwargs:
            kwargs = {arg: arg for arg in args}
            args = ()
        super(ReflexiveDict, self).__init__(*args, **kwargs)

    def __setitem__(self, key, value):
        super(ReflexiveDict, self).__setitem__(key, key)


#-------------------------------------------------------------------------------
# SeqDict


class SeqDict(AttrDict):
    '''An AttrDict whose items are treated as sequences.
    '''

    def update(self, *args, **kwargs):
        other = dict(dict_arg(*args, **kwargs))

        for key, val in other.items():
            if key not in self:
                self[key] = val
            else:
                typ = type(self[key])
                self[key] += typ(val)


#-------------------------------------------------------------------------------
# AssocDict


class AssocDict(collections.MutableMapping):
    '''Mapping maintained via an assoc list.
    '''
    __slots__ = ('_data')

    def __init__(self, *args, **kwargs):
        self._data = []
        self.update(*args, **kwargs)

    def __repr__(self):
        return repr(dict(self))

    def __getitem__(self, key):
        for _key, val in self._data:
            if key == _key:
                return val
        raise KeyError("Key '%s' not present" % str(key))

    def __setitem__(self, key, val):
        for k,(_key, _val) in enumerate(self._data):
            if key == _key:
                self._data[k] = (key, val)
                return
        self._data.append((key, val))

    def __delitem__(self, key):
        val = self[key]
        self._data.remove((key, val))

    def __iter__(self):
        keys = (key for key, val in self._data)
        return iter(keys)

    def __len__(self):
        return len(self._data)

    def update(self, *args, **kwargs):
        '''Preserves order if given an assoc list.
        '''
        arg = dict_arg(*args, **kwargs)
        if isinstance(arg, list):
          for key, val in arg:
              self[key] = val
        else:
            super(AssocDict, self).update(arg)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('AttrDict', 'UpdateDict', 'GroupDict', 'ReflexiveDict', 'SeqDict',
           'AssocDict', 'SetDict')

#-------------------------------------------------------------------------------
