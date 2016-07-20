import syn.base
import syn.base.b

#-------------------------------------------------------------------------------
# Base imports

def test_base_imports():
    assert syn.base.Base is syn.base.b.Base
    assert syn.base.Attr is syn.base.b.Attr
    assert syn.base.Attrs is syn.base.b.Attrs
    assert syn.base.This is syn.base.b.This

    assert syn.base.ListWrapper is syn.base.b.ListWrapper

    assert syn.base.create_hook is syn.base.b.create_hook
    assert syn.base.init_hook is syn.base.b.init_hook
    assert syn.base.coerce_hook is syn.base.b.coerce_hook
    assert syn.base.setstate_hook is syn.base.b.setstate_hook

    assert syn.base.Counter is syn.base.b.Counter

    assert syn.base.check_idempotence is syn.base.b.check_idempotence

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
