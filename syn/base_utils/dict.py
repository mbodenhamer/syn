''' Various dict extensions.
'''

#-------------------------------------------------------------------------------
# AttrDict


class AttrDict(dict):
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
# __all__

__all__ = ('AttrDict', 'UpdateDict')

#-------------------------------------------------------------------------------
