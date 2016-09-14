import operator as op

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
# Fuzzy logic

def fuzzy_and(*args):
    from .float import prod
    return prod(args)

def fuzzy_not(arg):
    return 1.0 - arg

def fuzzy_nand(*args):
    return fuzzy_not(fuzzy_and(*args))

def fuzzy_or(*args):
    return fuzzy_nand(*[fuzzy_not(arg) for arg in args])

def fuzzy_nor(*args):
    return fuzzy_not(fuzzy_or(*args))

def fuzzy_implies(a, b):
    return fuzzy_or(fuzzy_not(a), b)

def fuzzy_equiv(a, b):
    return fuzzy_and(fuzzy_implies(a, b),
                     fuzzy_implies(b, a))

def fuzzy_xor(a, b):
    return fuzzy_and(fuzzy_or(a, b),
                     fuzzy_not(fuzzy_equiv(a, b)))

#-------------------------------------------------------------------------------
# Collection logic

def collection_equivalent(A, B):
    return all(a in B for a in A) and all(b in A for b in B)

def collection_comp(A, B, item_func=op.eq, coll_func=all):
    return coll_func(item_func(a, b) for (a, b) in zip(A, B))

#-------------------------------------------------------------------------------
# __all__

__all__ = ('implies', 'equiv', 'xor', 'and_', 'or_', 'nand', 'nor',
           'fuzzy_and', 'fuzzy_not', 'fuzzy_nand', 'fuzzy_or', 'fuzzy_nor',
           'fuzzy_implies', 'fuzzy_equiv', 'fuzzy_xor',
           'collection_equivalent', 'collection_comp')

#-------------------------------------------------------------------------------
