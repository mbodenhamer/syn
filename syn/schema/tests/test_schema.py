import syn.schema
import syn.schema.b

#-------------------------------------------------------------------------------
# Schema imports

def test_schema_imports():
    assert syn.schema.SchemaNode is syn.schema.b.SchemaNode

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
