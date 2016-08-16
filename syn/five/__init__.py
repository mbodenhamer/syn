'''Additional Python 2/3 compatibility facilities.
'''
from .string import *
from .num import *
from six import PY2, PY3
from six.moves import xrange

# For convenience, not compatibility
SET = (set, frozenset)

from syn.base_utils import harvest_metadata, delete
with delete(harvest_metadata, delete):
    harvest_metadata('../metadata.yml')
