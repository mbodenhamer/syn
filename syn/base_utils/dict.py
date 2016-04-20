''' Various dict extensions.
'''
from functools import reduce

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

    def complement(self, key):
        universe = self.union()
        return universe.difference(self[key])

    def intersection(self):
        return set(reduce(set.intersection, self.values()))

    def union(self):
        return set(reduce(set.union, self.values()))


#-------------------------------------------------------------------------------
# __all__

__all__ = ('AttrDict', 'UpdateDict', 'GroupDict')

#-------------------------------------------------------------------------------
