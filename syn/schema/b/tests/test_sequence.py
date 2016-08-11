from syn.schema.b import SchemaNode

#-------------------------------------------------------------------------------
# SchemaNode

def test_schemanode():
    SchemaNode

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
