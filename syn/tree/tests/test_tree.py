import syn.tree
import syn.tree.b

#-------------------------------------------------------------------------------
# Tree imports

def test_tree_imports():
    assert syn.tree.Node is syn.tree.b.Node
    assert syn.tree.Tree is syn.tree.b.Tree

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
