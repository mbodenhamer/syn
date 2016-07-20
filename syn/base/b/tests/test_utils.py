from nose.tools import assert_raises
from syn.base.b import Counter

#-------------------------------------------------------------------------------
# Counter

def test_counter():
    c = Counter()
    c()
    assert c.peek() == 0
    for i in range(3): c()
    assert c.peek() == 3
    c.validate()
    c.threshold = 1
    assert_raises(ValueError, c.validate)

    c2 = Counter(threshold = 2)
    c2(); c2()
    assert c2.peek() == 1
    assert c2() == 2
    c2.validate()
    assert c2() == 0

    c3 = Counter(resets = [c])
    assert c() == 4
    assert c3() == 0
    assert c() == 0
    assert c() == 1
    assert c3() == 1
    assert c() == 0

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
