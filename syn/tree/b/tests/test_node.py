from nose.tools import assert_raises
from syn.tree.b import Node, TreeError
from syn.base.b.tests.test_base import check_idempotence

#-------------------------------------------------------------------------------
# Tree Node

def treenode_tst_1(cls):
    n1 = cls(_name='n1')
    n2 = cls(_name='n2')
    n3 = cls(_name='n3')
    n1.add_child(n2)

    assert n2 in n1._children
    assert n2._parent is n1
    assert not n2._children
    assert not n1._parent

    n1.add_child(n3, 0)
    assert n3 == n1._children[0]

    check_idempotence(n1)

    n1.validate()
    n1.set_child_parents(1, True)
    assert all(c._parent == 1 for c in n1._children)
    assert all(c._parent == 1 for c in n2._children)
    n1.validate()
    #assert_raises(TypeError, n1.validate)

def test_node():
    n = Node()
    assert n._children == []
    assert n._parent is None
    assert n._id is None
    assert n._name is None
    assert bool(n) is True

    obj = Node(_id = 4545, _name = 'foonode')
    assert obj._children == []
    assert obj._parent is None
    assert obj._id == 4545
    assert obj._name == 'foonode'

    assert obj.get_children() is obj._children
    assert obj.get_parent() is obj._parent
    assert obj.get_id() is obj._id
    assert obj.get_name() is obj._name

    treenode_tst_1(Node)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
