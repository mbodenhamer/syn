from syn.five import xrange
from syn.type.a import TYPE_REGISTRY

SAMPLES = 5

#-------------------------------------------------------------------------------
# Registry

def test_registry():
    for typ, reg in TYPE_REGISTRY.items():
        for k in xrange(SAMPLES):
            samp = reg.generate()
            assert isinstance(samp, typ)

    assert TYPE_REGISTRY[int].coerce('5') == 5

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
