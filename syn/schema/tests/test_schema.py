from syn.schema import sequence
import syn.schema.b.sequence

#-------------------------------------------------------------------------------
# Schema imports

def test_schema_imports():
    assert sequence.SchemaNode is syn.schema.b.sequence.SchemaNode

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
