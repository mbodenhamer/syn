'''Additional Python 2/3 compatibility facilities.
'''
from .string import *
from .num import *
from six import PY2, PY3

# range-related
from six.moves import xrange
range = lambda *args, **kwargs: list(xrange(*args, **kwargs))

if PY2:
    raw_input = raw_input
    import itertools
    izip = itertools.izip
    imap = itertools.imap
    ifilter = itertools.ifilter
else:
    raw_input = input
    izip = zip
    imap = map
    ifilter = filter

# For convenience, not compatibility
SET = (set, frozenset)

# from syn.base_utils import harvest_metadata, delete
# with delete(harvest_metadata, delete):
#     harvest_metadata('../metadata.yml')
