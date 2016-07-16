from syn.tree.b import Node

#-------------------------------------------------------------------------------
# Tree Node

def test_node():
    Node

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
