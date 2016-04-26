'''Utilities for determining hashability and converting to hashable objects.
'''

def is_hashable(obj):
    try:
        hash(obj)
    except TypeError:
        return False
    return True


#-------------------------------------------------------------------------------
# __all__

__all__ = ('is_hashable',)

#-------------------------------------------------------------------------------
