from .conf import *
from .vars import *

from syn.base_utils import harvest_metadata, delete
with delete(harvest_metadata, delete):
    harvest_metadata('../metadata.yml')
