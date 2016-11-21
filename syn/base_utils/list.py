from syn.five import xrange, STR
from collections import Sequence, MutableSequence

from .logic import implies
from .py import getitem

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
# IterableList


class IterableList(list):
    def __init__(self, values, position=0, position_mark=None):
        super(IterableList, self).__init__(values)
        self.position = position
        self.position_mark = (position_mark if position_mark is not None 
                              else self.position)

    def _check_position(self):
        if self.position >= len(self) or self.position < 0:
            raise StopIteration()

    def consume(self, n):
        self.seek(n, 1)

    def copy(self):
        return type(self)(list(self), position=self.position,
                          position_mark=self.position_mark)

    def displacement(self):
        return self.position - self.position_mark

    def empty(self):
        return len(self) == 0 or self.position >= len(self)

    def mark(self):
        self.position_mark = self.position

    def __next__(self):
        return self.next()

    def next(self):
        ret = self.peek()
        self.seek(1, 1)
        return ret

    def peek(self, n=None, safe=True):
        if n is not None:
            self.seek(n, 1)
        
        try:
            self._check_position()
        except StopIteration:
            if safe:
                if n is not None:
                    self.position += -n
                return
            raise StopIteration()

        ret = self[self.position]
        if n is not None:
            self.seek(-n, 1)
        return ret

    def previous(self):
        self.seek(-1, 1)
        ret = self.peek()
        return ret

    def reset(self):
        self.position = self.position_mark
        self._check_position()

    def seek(self, n, mode=0):
        if mode == 0:
            self.position = n
        elif mode == 1:
            self._check_position()
            self.position += n
        elif mode == 2:
            self.position = len(self) - n - 1
        else:
            raise ValueError("Invalid mode value '%d'" % mode)

    def take(self, n):
        self._check_position()
        if n > 0:
            self.peek(n-1, safe=False)
            ret = self[self.position:self.position+n]
            self.consume(n)
            return ret
        return []


#-------------------------------------------------------------------------------
# DefaultList


class DefaultList(list):
    def __init__(self, default, *args, **kwargs):
        self.assign = getitem(kwargs, 'assign', True, delete=True)
        super(DefaultList, self).__init__(*args, **kwargs)
        self.default = default

    def __getitem__(self, index):
        try:
            return super(DefaultList, self).__getitem__(index)
        except IndexError:
            ret = self._default()
            if self.assign:
                self[index] = ret
            return ret

    def __setitem__(self, index, value):
        try:
            super(DefaultList, self).__setitem__(index, value)
        except IndexError:
            self._set(index, value)

    def _default(self):
        if isinstance(self.default, type):
            return self.default()
        return self.default

    def _set(self, index, value):
        if index < len(self):
            raise IndexError('Invalid index: {}'.format(index))

        n_fill = index - len(self)
        for _ in xrange(n_fill):
            self.append(self._default())
        self.append(value)


#-------------------------------------------------------------------------------
# Query Utilities

def is_proper_sequence(seq):
    if not isinstance(seq, Sequence):
        return False
    return not isinstance(seq, STR)

def is_flat(seq):
    if not isinstance(seq, Sequence):
        raise TypeError("seq is not a Sequence")
    return all(implies(isinstance(e, Sequence), 
                       isinstance(e, STR + (bytes,))) 
               for e in seq)

def is_unique(seq):
    '''Returns True if every item in the seq is unique, False otherwise.'''
    try:
        s = set(seq)
        return len(s) == len(seq)
    except TypeError:
        buf = []
        for item in seq:
            if item in buf:
                return False
            buf.append(item)
        return True

#-------------------------------------------------------------------------------
# Non-Modification Utilities

def indices_removed(lst, idxs):
    '''Returns a copy of lst with each index in idxs removed.'''
    ret = [item for k,item in enumerate(lst) if k not in idxs]
    return type(lst)(ret)

def flattened(seq):
    if not is_proper_sequence(seq):
        return [seq]
    if is_flat(seq):
        return list(seq)
    if len(seq) == 1:
        return flattened(seq[0])
    else:
        ret = flattened(seq[0])
        ret.extend(flattened(seq[1:]))
        return ret

#-------------------------------------------------------------------------------
# __all__

__all__ = ('ListView', 'IterableList', 'DefaultList',
           'is_proper_sequence', 'is_flat', 'is_unique',
           'indices_removed', 'flattened')

#-------------------------------------------------------------------------------
