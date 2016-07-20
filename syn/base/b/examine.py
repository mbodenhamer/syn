from syn.base_utils import assert_deepcopy_idempotent, assert_pickle_idempotent 

#-------------------------------------------------------------------------------
# Idempotence

def check_idempotence(obj):
    assert_deepcopy_idempotent(obj)
    assert_pickle_idempotent(obj)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('check_idempotence',)

#-------------------------------------------------------------------------------
