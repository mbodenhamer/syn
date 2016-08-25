from operator import attrgetter
from nose.tools import assert_raises
from syn.tree.b import Tree, Node, TreeError, do_nothing, identity
from syn.base.b import check_idempotence, Attr
from syn.base_utils import get_typename
from syn.tree.b.tests.test_node import Tst2, tree_node_from_nested_list,\
    tree_node_from_nested_list_types

#-------------------------------------------------------------------------------
# Tree

#-----------------------------------------------------------
# Tree Test 1

def tree_tst_1(treecls):
    cls = treecls._attrs.types['root'].type
    clsname = get_typename(cls)
    n1 = cls(_name='n1', _id=0)
    n2 = cls(_name='n2', _id=1)
    n3 = cls(_name='n3', _id=2)
    n4 = cls(_name='n4', _id=3)
    n5 = cls(_name='n5', _id=4)
    n6 = cls(_name='n6', _id=5)

    n1.add_child(n2)
    n1.add_child(n3)

    assert list(n1.siblings()) == []
    assert list(n2.siblings()) == [n3]
    assert list(n3.siblings()) == [n2]

    obj = treecls(n1)
    check_idempotence(obj)

    assert obj.nodes == [n1, n2, n3]
    assert obj.node_types == [clsname]
    assert obj.id_dict == {0: n1, 1: n2, 2: n3}
    assert obj.type_dict == {clsname: [n1, n2, n3]}

    assert_raises(TreeError, obj.add_node, n3)
    assert_raises(TreeError, obj.add_node, n4, parent=n5)
    obj.add_node(n4, parent=n3)
    
    assert n4 in obj.nodes
    assert n4 in n3._children
    assert n4._parent is n3

    assert_raises(TreeError, obj.add_node, n5, parent_id=100)
    obj.add_node(n5, parent_id=1)

    assert n5 in obj.nodes
    assert n5 in n2._children
    assert n5._parent is n2

    obj.add_node(n6)
    assert n6 in obj.nodes
    assert n6 in n5._children
    assert n6._parent is n5

    assert obj.nodes == [n1, n2, n3, n4, n5, n6]
    assert obj.node_types == [clsname]
    assert obj.id_dict == {0: n1, 1: n2, 2: n3, 3:n4, 4:n5, 5:n6}
    assert obj.type_dict == {clsname: [n1, n2, n3, n4, n5, n6]}
    
    
    for _id,node in enumerate([n1, n2, n3, n4, n5, n6]):
        assert obj.get_node_by_id(_id) == obj._get_node_by_id(_id)
        assert obj.get_node_by_id(_id) == node
    assert obj.get_node_by_id(100) is None    
    assert obj.get_node_by_id(-1) is None    
    

    assert_raises(TypeError, obj.depth_first, FooType = do_nothing)
    assert_raises(TypeError, obj._check_search_kwarg_types, 
                  {Tst2: do_nothing})
    assert_raises(TypeError, obj._check_search_kwarg_types, {0: do_nothing})

    assert list(n1.descendants()) == [n2, n5, n6, n3, n4]

    accum = []
    def collect(node):
        accum.append(node._id)
    
    obj.depth_first(collect)
    assert accum == [0, 1, 4, 5, 2, 3]

    accum = []
    obj.depth_first(**{clsname: collect})
    assert accum == [0, 1, 4, 5, 2, 3]

    accum = []
    obj.search_rootward(collect)
    assert accum == [0]

    accum = []
    obj.search_rootward(**{'current_node': n5, 
                           clsname: collect})
    assert accum == [4, 1, 0]

    def stop(node):
        return node._id == 3
    def get(node):
        return node._name

    assert obj.depth_first(stop_test = stop, _return = get) == 'n4'
    assert obj.search_rootward(stop_test = stop, _return = get) is None
    assert obj.search_rootward(current_node = n4, stop_test = stop, 
                               _return = get) == 'n4'
    assert obj.search_rootward(current_node = n6, stop_test = stop,
                               _return = get) is None


    n7 = cls(_name='n7', _id=6)
    n8 = cls(_name='n8', _id=7)

    n7.add_child(n8)
    obj.replace_node(n5, n7)

    assert n2._children == [n7]
    assert n7._parent is n2
    assert n7._children == [n8]
    assert n8._parent is n7

    assert n5._children == [n6]
    assert n6._parent is n5
    assert n5._parent is None

    assert obj.nodes == [n1, n2, n3, n4, n7, n8]
    assert obj.node_types == [clsname]
    assert obj.id_dict == {0: n1, 1: n2, 2: n3, 3:n4, 6:n7, 7:n8}
    assert obj.type_dict == {clsname: [n1, n2, n3, n4, n7, n8]}


    assert_raises(TreeError, obj.remove_node, n5)
    assert_raises(TreeError, obj.replace_node, n5, n7)

    obj.remove_node(n2)
    assert n1._children == [n3]
    assert n2._parent is None
    assert n2._children == [n7]
    assert n7._parent is n2

    assert obj.nodes == [n1, n3, n4]
    assert obj.node_types == [clsname]
    assert obj.id_dict == {0: n1, 2: n3, 3:n4}
    assert obj.type_dict == {clsname: [n1, n3, n4]}


    assert_raises(TreeError, obj.replace_node, n1, n7)
    assert_raises(TreeError, obj.replace_node, n3, n7)

    obj.replace_node(n1, n2)
    assert n1._children == [n3]
    assert n3._parent is n1

    assert obj.root is n2
    assert obj.nodes == [n2, n7, n8]
    assert obj.node_types == [clsname]
    assert obj.id_dict == {1: n2, 6: n7, 7:n8}
    assert obj.type_dict == {clsname: [n2, n7, n8]}
    

    obj.rebuild()
    assert obj.root is n2
    assert obj.nodes == [n2, n7, n8]
    assert obj.node_types == [clsname]
    assert obj.id_dict == {1: n2, 6: n7, 7:n8}
    assert obj.type_dict == {clsname: [n2, n7, n8]}


    obj.remove_node(n2)
    assert obj.root is None
    assert obj.nodes == []
    assert obj.node_types == []
    assert obj.id_dict == {}
    assert obj.type_dict == {}

#-----------------------------------------------------------
# Tree Test 2

def tree_tst_2(treecls):
    from syn.base_utils import seq_list_nested

    b = 3
    d = 4 # 121 nodes
    # d = 6 # 1093 nodes
    # d = 7 # 3280 nodes
    # d = 8 # Almost 10,000 nodes

    lst, N = seq_list_nested(b, d, top_level=False)

    root = tree_node_from_nested_list(lst[0], lst[1])
    assert isinstance(root, Node)

    tree1 = treecls(root)
    base_id = 0

    check_idempotence(tree1)

    assert len(tree1.nodes) == N
    assert tree1.node_types == ['Tst1',]
    assert sorted(tree1.id_dict.keys()) == list(range(base_id,base_id + N))
    assert list(tree1.type_dict.keys()) == ['Tst1']
    assert sorted(tree1.type_dict['Tst1'], key=attrgetter('_id')) == \
        sorted(tree1.nodes, key=attrgetter('_id'))

    accum = []
    def collect(node):
        accum.append(node.value)
    tree1.depth_first(collect)
    assert sum(accum) == sum(range(1, N+1))

    while tree1.root._children:
        tree1.remove_node(tree1.root._children[0])

    assert tree1.nodes == [tree1.root]
    assert tree1.root._children == []

    mod = 4
    base_id = 0
    sproot = tree_node_from_nested_list_types(lst[0], lst[1], mod)
    tree2 = Tree(sproot)
    
    assert len(tree2.nodes) == N
    assert tree2.node_types == ['Tst1', 'Tst2']
    assert sorted(tree2.id_dict.keys()) == list(range(base_id,base_id+N))
    assert sorted(tree2.type_dict.keys()) == sorted(['Tst1', 'Tst2'])
    assert sorted(tree2.type_dict['Tst1'] + 
                  tree2.type_dict['Tst2'], key=attrgetter('_id')) == \
        sorted(tree2.nodes, key=attrgetter('_id'))

    accum = []
    tree2.depth_first(collect)
    assert sum(accum) == sum(range(1, N+1))
    
    accum = []
    tree2.depth_first(Tst2 = collect)
    if N % mod != 0:
        assert sum(accum) == sum(range(mod, N, mod))

#-----------------------------------------------------------
# Tree

def test_tree():
    # Test that inequal roots mean inequal Trees
    n1 = Node()
    n2 = Node(_id=2)

    t1 = Tree(n1)
    t2 = Tree(n2)

    assert n1 != n2
    assert t1 != t2

    t3 = Tree()
    t3.validate()
    assert t3 == t1

    # In-depth tree tests
    tree_tst_1(Tree) # basic tree operations
    tree_tst_2(Tree) # test with a moderate/large number of nodes

    # Miscellaneous tests
    assert identity(5) == 5

    n3 = Node(_id = 3)
    t2.add_node(n3, parent=n2)
    n3._parent = None
    assert_raises(TreeError, t2.remove_node, n3)
    assert_raises(TreeError, t2.replace_node, n3, n1)

#-------------------------------------------------------------------------------
# Test root node validation

rnv_accum = []
class Root1(Node):
    def validate(self):
        super(Root1, self).validate()
        rnv_accum.append(1)

class RNVTree(Tree):
    _attrs = dict(root = Attr(Root1))

def test_root_validation():
    RNVTree(Root1())
    assert sum(rnv_accum) == len(rnv_accum) == 1 # just a sanity check

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
