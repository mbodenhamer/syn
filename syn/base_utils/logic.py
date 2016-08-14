#-------------------------------------------------------------------------------
# Propositional logic

def implies(a, b):
    return (not a) or b

def equiv(a, b):
    return (a == b and b == a)

#-------------------------------------------------------------------------------
# Collection logic

def collection_equivalent(A, B):
    return all(a in B for a in A) and all(b in A for b in B)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('implies', 'equiv',
           'collection_equivalent')

#-------------------------------------------------------------------------------
