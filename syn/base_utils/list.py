from syn.five import xrange
from collections import MutableSequence

#-------------------------------------------------------------------------------
# ListView


class ListView(MutableSequence):
    '''A list view.'''
    def __init__(self, lst, start, end):
        if not isinstance(lst, list):
            raise TypeError("Parameter lst must be type list")

        self.list = lst
        self.start = start
        self.end = end
        if self.end < 0:
            self.end = len(self.list) + self.end + 1

        if self.end < self.start:
            raise ValueError('End less than start')

        if not 0 <= self.start < len(self.list):
            raise ValueError('Invalid start position')

        if not 0 <= self.end <= len(self.list):
            raise ValueError('Invalid end position')

    def _correct_idx(self, idx):
        if idx < 0:
            return self.end + idx
        return self.start + idx

    def __getitem__(self, idx):
        idx = self._correct_idx(idx)
        if not self.start <= idx < self.end:
            raise IndexError("index out of range")
        return self.list[idx]

    def __setitem__(self, idx, value):
        idx = self._correct_idx(idx)
        if not self.start <= idx < self.end:
            raise IndexError("index out of range")
        self.list[idx] = value

    def __delitem__(self, idx):
        idx = self._correct_idx(idx)
        if not self.start <= idx < self.end:
            raise IndexError("index out of range")
        self.list.pop(idx)
        self.end -= 1

    def __iter__(self):
        for k in xrange(self.start, self.end):
            yield self.list[k]

    def __len__(self):
        return self.end - self.start

    def insert(self, idx, obj):
        idx = self._correct_idx(idx)
        self.list.insert(idx, obj)
        self.end += 1


#-------------------------------------------------------------------------------
# __all__

__all__ = ('ListView',)

#-------------------------------------------------------------------------------
