import syn.python as spy
import syn.python.b as bspy

#-------------------------------------------------------------------------------
# Imports

def test_imports():
    assert spy.PythonNode is bspy.PythonNode

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
