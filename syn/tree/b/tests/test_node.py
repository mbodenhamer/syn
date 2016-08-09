from nose.tools import assert_raises
from syn.base.b import Attr
from syn.tree.b import Node, TreeError
from syn.base.b.tests.test_base import check_idempotence
from syn.base_utils import assert_equivalent, assert_inequivalent, \
    assert_type_equivalent

#-------------------------------------------------------------------------------
# Tree Node Test 1

def treenode_tst_1(cls):
    n1 = cls(_name='n1')
    n2 = cls(_name='n2')
    n3 = cls(_name='n3')

    assert n1.node_count() == 1
    n1.add_child(n2)
    assert n1.node_count() == 2

    assert n2 in n1._children
    assert n2._parent is n1
    assert not n2._children
    assert not n1._parent

    n1.add_child(n3, 0)
    assert n3 == n1._children[0]
    assert n1.node_count() == 3

    check_idempotence(n1)

    n1.validate()
    n1.set_child_parents(1, True)
    assert all(c._parent == 1 for c in n1._children)
    assert all(c._parent == 1 for c in n2._children)
    assert_raises(TypeError, n1.validate)

#-------------------------------------------------------------------------------
# Tree Node Test 2

class Tst1(Node):
    _attrs = dict(value = Attr(int))

def tree_node_from_nested_list(x, lst):
    ret = Tst1(_name= 'n{}'.format(x), value = x)
    assert len(lst) % 2 == 0 or not any(isinstance(x, list) for x in lst)
    
    if not any(isinstance(x, list) for x in lst):
        for x in lst:
            child = Tst1(_name = 'n{}'.format(x), value = x)
            ret.add_child(child)
    else:
        for i in range(0, len(lst), 2):
            x, sublst = lst[i], lst[i+1]
            child = tree_node_from_nested_list(x, sublst)
            ret.add_child(child)

    return ret

class Tst2(Tst1):
    pass

def tree_node_from_nested_list_types(x, lst, mod=4):
    if x % mod == 0:
        ret = Tst2(_name= 'n{}'.format(x), value = x)
    else:
        ret = Tst1(_name= 'n{}'.format(x), value = x)
    assert len(lst) % 2 == 0 or not any(isinstance(x, list) for x in lst)
    
    if not any(isinstance(x, list) for x in lst):
        for x in lst:
            if x % mod == 0:
                child = Tst2(_name = 'n{}'.format(x), value = x)
            else:
                child = Tst1(_name = 'n{}'.format(x), value = x)
            ret.add_child(child)
    else:
        for i in range(0, len(lst), 2):
            x, sublst = lst[i], lst[i+1]
            child = tree_node_from_nested_list_types(x, sublst, mod)
            ret.add_child(child)

    return ret

def treenode_tst_2(cls):
    import math
    from syn.base_utils import seq_list_nested

    b = 3
    d = 4 # 121 nodes

    lst, N = seq_list_nested(b, d, top_level=False)

    root = tree_node_from_nested_list(lst[0], lst[1])
    assert isinstance(root, Node)
    assert isinstance(root, Tst1)

    nodes = root.collect_nodes()
    assert len(nodes) == N
    check_idempotence(root)

    mod = 4
    sproot = tree_node_from_nested_list_types(lst[0], lst[1], mod)
    specials = sproot.collect_by_type(Tst2)

    assert len(specials) == int(math.floor(N/mod))

    special = sproot.find_type(Tst2)
    assert special.value == 16
    assert sproot.find_type(Tst2, True) is None

    n79l = sproot.collect_nodes('value', 79)
    assert len(n79l) == 1
    assert n79l[0].value == 79

    gt50l = sproot.collect_nodes(key = lambda n: n.value > 50)
    assert len(gt50l) == N - 50
    assert all(n.value > 50 for n in gt50l)

    assert_raises(TypeError, sproot.collect_nodes, key=1)

#-------------------------------------------------------------------------------
# Tree Node Test 3

def treenode_tst_3(cls):
    n5 = cls(_id = 5)
    n4 = cls(_id = 4)
    n3 = cls(n4, _id = 3)
    n2 = cls(_id = 2)
    n1 = cls(n2, n3, n5, _id = 1)

    assert n4.collect_rootward() == [n4, n3, n1]

    assert n1._children == [n2, n3, n5]
    assert n3._children == [n4]
    assert n2._parent is n1
    assert n3._parent is n1
    assert n4._parent is n3
    assert n5._parent is n1
    
    assert n5.siblings() == [n2, n3]
    assert n4.siblings() == []
    assert n3.siblings() == [n2, n5]
    assert n2.siblings() == [n3, n5]
    assert n1.siblings() == []

    assert n1.descendants() == [n2, n3, n4, n5]
    assert n2.descendants() == []
    assert n3.descendants() == [n4]
    assert n4.descendants() == []
    assert n5.descendants() == []

    n1.remove_child(n5)
    assert n1._children == [n2, n3]
    assert n5._parent is None
    assert n5.siblings() == []
    assert n1.descendants() == [n2, n3, n4]
    
    assert_raises(TreeError, n1.remove_child, n5)

#-------------------------------------------------------------------------------
# Tree Node

def test_tree_node():
    n = Node()
    assert n._children == []
    assert n._parent is None
    assert n._id is None
    assert n._name is None
    assert bool(n) is True
    assert_equivalent(n, Node())

    obj = Node(_id = 4545, _name = 'foonode')
    assert obj._children == []
    assert obj._parent is None
    assert obj._id == 4545
    assert obj._name == 'foonode'

    assert obj.get_children() is obj._children
    assert obj.get_parent() is obj._parent
    assert obj.get_id() is obj._id
    assert obj.get_name() is obj._name
    assert_inequivalent(obj, n)

    treenode_tst_1(Node)
    treenode_tst_2(Node)
    treenode_tst_3(Node)

#-------------------------------------------------------------------------------
# must_be_root

class Root1(Node):
    _opts = dict(must_be_root = True)

def test_node_must_be_root():
    n2 = Node(_id = 2)
    r1 = Root1(n2, _id = 1)

    r1.validate()

    r2 = Root1(_id = 3)
    r1.add_child(r2)
    assert_raises(TreeError, r2.validate)
    assert_raises(TreeError, r1.validate)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
