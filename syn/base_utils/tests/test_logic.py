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

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
