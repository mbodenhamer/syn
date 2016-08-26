from operator import attrgetter
from nose.tools import assert_raises
from syn.base import Attr
from syn.tree.b import Tree
from syn.tree.b import Node as Node_
from syn.tree.b.query import Query, Type, Root, Self, Child, Descendant
import syn.type.a

class Node(Node_):
    _attrs = dict(name = Attr(str))

#-------------------------------------------------------------------------------
# Query

def test_query():
    q = Query()
    assert_raises(NotImplementedError, q, 1)

#-------------------------------------------------------------------------------
# Type

def test_type():
    t = Type()
    assert isinstance(t.type, syn.type.a.AnyType)

    t = Type(Node)
    assert isinstance(t.type, syn.type.a.TypeType)
    assert t.type.type is Node

#-------------------------------------------------------------------------------
# Axes

def test_axes():
    n5 = Node(name = 'n5')
    n4 = Node(name = 'n4')
    n3 = Node(n4, name = 'n3')
    n2 = Node(name = 'n2')
    n1 = Node(n2, n3, n5, name = 'n1')

    t = Tree(n1)
             
    assert list(t.root.depth_first(attrgetter('name'))) == \
        ['n1', 'n2', 'n3', 'n4', 'n5']

    q = Root() # /   (or root::node())
    assert t.find_one(q) is n1
    assert list(t.query(q)) == [n1]
    assert t.find_one(q, n5) is n1
    assert list(t.query(q, n5)) == [n1]

    q = Self() # .   (or self::node())
    assert t.find_one(q) is n1
    assert list(t.query(q)) == [n1]
    assert t.find_one(q, n5) is n5
    assert list(t.query(q, n5)) == [n5]

    q = Child() # ./*
    assert list(t.query(q)) == [n2, n3, n5]
    assert list(t.query(q, n3)) == [n4]

    q = Child(Root()) # /*
    assert list(t.query(q)) == [n2, n3, n5]
    assert list(t.query(q, n3)) == [n2, n3, n5]

    q = Child(Child()) # ./*/*
    assert list(t.query(q)) == [n4]
    assert list(t.query(q, n3)) == []
    assert t.find_one(q, n3) is None

    q = Child(Child(Self())) # ./*/*
    assert list(t.query(q)) == [n4]
    assert list(t.query(q, n3)) == []
    assert t.find_one(q, n3) is None

    q = Descendant(Root(), include_self=True) # //*
    assert list(t.query(q)) == [n1, n2, n3, n4, n5]
    assert list(t.query(q, n3)) == [n1, n2, n3, n4, n5]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
