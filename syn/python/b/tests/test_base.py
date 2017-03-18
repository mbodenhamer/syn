from syn.python.b import PythonNode

#-------------------------------------------------------------------------------
# Base Class

def test_pythonnode():
    assert sorted(PythonNode._groups['ast_attr']) == ['col_offset', 'lineno']
    assert PythonNode._groups['ast_convert_attr'] == set([])
    assert PythonNode._groups['eq_exclude'] == {'_parent'}

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
