import operator as op
from functools import partial
from syn.base_utils import feq

#-------------------------------------------------------------------------------
# Propositional logic

def test_implies():
    from syn.base_utils import implies
    assert implies(True, False) is False
    assert implies(True, True) is True
    assert implies(False, False) is True
    assert implies(False, True) is True

def test_equiv():
    from syn.base_utils import equiv

    assert equiv(1, 1)
    assert not equiv(1, 2)

    class Foo(object):
        def __init__(self, **kwargs):
            self.dct = kwargs
        
        def __eq__(self, x):
            ret = True
            for k in self.dct:
                if k in x.dct:
                    ret = ret and (self.dct[k] == x.dct[k])
                else:
                    return False
            return ret

    x = Foo(a=1, b=2)
    y = Foo(a=1, b=3)
    z = Foo(a=1, b=2, c=3)

    assert x == z
    assert not z == x
    assert not x == y
    assert x == x

    assert equiv(x, x)
    assert not equiv(x, y)
    assert not equiv(x, z)

def test_xor():
    from syn.base_utils import xor

    assert xor(True, False)
    assert xor(False, True)
    assert not xor(True, True)
    assert not xor(False, False)

def test_and_():
    from syn.base_utils import and_

    assert and_(True, True, True)
    assert not and_(True, True, False)

def test_or_():
    from syn.base_utils import or_

    assert or_(True, True, True)
    assert or_(False, False, True)
    assert not or_(False, False, False)

def test_nand():
    from syn.base_utils import nand

    assert not nand(True, True, True)
    assert nand(True, True, False)
    assert nand(False, False, False)

def test_nor():
    from syn.base_utils import nor

    assert not nor(True, True, True)
    assert not nor(False, False, True)
    assert nor(False, False, False)

#-------------------------------------------------------------------------------
# Fuzzy logic

def test_fuzzy_and():
    from syn.base_utils import fuzzy_and

    assert feq(fuzzy_and(1, 1, 1), 1)
    assert feq(fuzzy_and(1, 1, 0), 0)

def test_fuzzy_not():
    from syn.base_utils import fuzzy_not

    assert feq(fuzzy_not(1), 0)
    assert feq(fuzzy_not(0), 1)

def test_fuzzy_nand():
    from syn.base_utils import fuzzy_nand

    assert feq(fuzzy_nand(1, 1, 1), 0)
    assert feq(fuzzy_nand(1, 1, 0), 1)
    assert feq(fuzzy_nand(0, 0, 0), 1)

def test_fuzzy_or():
    from syn.base_utils import fuzzy_or

    assert feq(fuzzy_or(1, 1, 1), 1)
    assert feq(fuzzy_or(1, 1, 0), 1)
    assert feq(fuzzy_or(1, 0, 0), 1)
    assert feq(fuzzy_or(0, 0, 0), 0)

def test_fuzzy_nor():
    from syn.base_utils import fuzzy_nor

    assert feq(fuzzy_nor(1, 1, 1), 0)
    assert feq(fuzzy_nor(1, 1, 0), 0)
    assert feq(fuzzy_nor(1, 0, 0), 0)
    assert feq(fuzzy_nor(0, 0, 0), 1)

def test_fuzzy_implies():
    from syn.base_utils import fuzzy_implies

    assert feq(fuzzy_implies(0, 0), 1)
    assert feq(fuzzy_implies(0, 1), 1)
    assert feq(fuzzy_implies(1, 0), 0)
    assert feq(fuzzy_implies(1, 1), 1)

def test_fuzzy_equiv():
    from syn.base_utils import fuzzy_equiv

    assert feq(fuzzy_equiv(0, 0), 1)
    assert feq(fuzzy_equiv(0, 1), 0)
    assert feq(fuzzy_equiv(1, 0), 0)
    assert feq(fuzzy_equiv(1, 1), 1)

def test_fuzzy_xor():
    from syn.base_utils import fuzzy_xor

    assert feq(fuzzy_xor(0, 0), 0)
    assert feq(fuzzy_xor(0, 1), 1)
    assert feq(fuzzy_xor(1, 0), 1)
    assert feq(fuzzy_xor(1, 1), 0)

#-------------------------------------------------------------------------------
# Collection logic

def test_collection_equivalent():
    from syn.base_utils import collection_equivalent as ce

    assert ce([], ())
    assert ce([1, 2], [1, 2])
    assert ce([1, 2], [2, 1])
    assert ce((1, 2, 3, 4), {2, 1, 4, 3})

    assert not ce([], [1])
    assert not ce([1], [2, 1])

def test_collection_comp():
    from syn.base_utils import collection_comp as cc
    from syn.base_utils import feq

    assert cc([1, 2], [1, 2])
    assert not cc([2, 1], [1, 2])
    assert not cc([2, 1], [1, 2], coll_func=any)
    assert cc([2, 1], [1, 2], op.ne)
    assert not cc([2, 2], [1, 2], op.ne)
    assert not cc([2, 2], [1, 2], op.eq)
    assert cc([2, 2], [1, 2], coll_func=any)
    assert cc([2, 2], [1, 2], op.ne, any)

    assert cc([], ())
    assert not cc([], (), coll_func=any)

    assert not cc([1.1, 2.2], [1.1, 2.22])
    assert cc([1.1, 2.2], [1.1, 2.22], partial(feq, tol=5e-2))

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
