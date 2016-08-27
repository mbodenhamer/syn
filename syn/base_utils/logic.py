#-------------------------------------------------------------------------------
# Propositional logic

def implies(a, b):
    return (not a) or b

def equiv(a, b):
    return (a == b and b == a)

def xor(a, b):
    return (a or b) and not equiv(a, b)

def and_(*args):
    for arg in args:
        if not arg:
            return False
    return True

def or_(*args):
    for arg in args:
        if arg:
            return True
    return False

def nand(*args):
    return not and_(*args)

def nor(*args):
    return not or_(*args)

#-------------------------------------------------------------------------------
# Collection logic

def collection_equivalent(A, B):
    return all(a in B for a in A) and all(b in A for b in B)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('implies', 'equiv', 'xor', 'and_', 'or_', 'nand', 'nor',
           'collection_equivalent')

#-------------------------------------------------------------------------------
