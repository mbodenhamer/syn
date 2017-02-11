from operator import attrgetter
from nose.tools import assert_raises
from syn.base import Attr
from syn.tree.b import Tree
from syn.tree.b import Node as Node_
from syn.tree.b.query import Query, Type, Root, Self, Child, Descendant, \
    Ancestor, Parent, Sibling, Following, Preceding, Attribute, Where, \
    Predicate, Any, Position, Name, POSITION, Function, Value, Eq, Ne, Lt, Le, \
    Gt, Ge, Identity
from syn.base_utils import assign
import syn.type.a

class Node(Node_):
    _attrs = dict(name = Attr(str))

#-------------------------------------------------------------------------------
# Query

def test_query():
    q = Query()
    assert list(q(1)) == []

#-------------------------------------------------------------------------------
# Type

def test_type():
    t = Type()
    assert isinstance(t.type, syn.type.a.AnyType)

    t = Type(type=Node)
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

    q = Root() # /   (or root::)
    assert t.find_one(q) is n1
    assert list(t.query(q)) == [n1]
    assert t.find_one(q, n5) is n1
    assert list(t.query(q, n5)) == [n1]

    q = Self() # .   (or self::)
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

    q = Child(Type(Child())) # ./node()/*
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

    q = Descendant(Root()) # /descendant::
    assert list(t.query(q)) == [n2, n3, n4, n5]
    assert list(t.query(q, n3)) == [n2, n3, n4, n5]

    q = Descendant() # descendant::
    assert list(t.query(q)) == [n2, n3, n4, n5]
    assert list(t.query(q, n3)) == [n4]

    q = Ancestor() # ancestor::
    assert list(t.query(q)) == []
    assert list(t.query(q, n3)) == [n1]
    assert list(t.query(q, n4)) == [n3, n1]

    q = Ancestor(include_self=True) # ancestor-or-self::
    assert list(t.query(q)) == [n1]
    assert list(t.query(q, n3)) == [n3, n1]
    assert list(t.query(q, n4)) == [n4, n3, n1]

    q = Child(Ancestor()) # ancestor::/*
    assert list(t.query(q)) == []
    assert list(t.query(q, n3)) == [n2, n3, n5]
    assert list(t.query(q, n4)) == [n4, n2, n3, n5]

    q = Parent() # ..
    assert list(t.query(q)) == []
    assert list(t.query(q, n3)) == [n1]
    assert list(t.query(q, n4)) == [n3]
    
    q = Sibling(following=True) # following-sibling::
    assert list(t.query(q)) == []
    assert list(t.query(q, n3)) == [n5]
    assert list(t.query(q, n2)) == [n3, n5]

    q = Sibling(preceding=True) # preceding-sibling::
    assert list(t.query(q)) == []
    assert list(t.query(q, n3)) == [n2]
    assert list(t.query(q, n5)) == [n3, n2]

    q = Preceding() # <<
    assert list(t.query(q)) == []
    assert list(t.query(q, n5)) == [n4, n3, n2, n1]

    q = Following() # >>
    assert list(t.query(q)) == [n2, n3, n4, n5]
    assert list(t.query(q, n5)) == []

    q = Attribute() # @
    assert list(t.query(q)) == [('name', 'n1')]
    assert list(t.query(q, n5)) == [('name', 'n5')]

    q = Attribute(Preceding()) # <<@
    assert list(t.query(q, n3)) == [('name', 'n2'), ('name', 'n1')]

#-------------------------------------------------------------------------------
# Predicates

def test_predicates():
    p = Predicate()
    assert_raises(NotImplementedError, p, 1)

    p = Any()
    assert p(1) is True

    p = Name('foo')
    assert p(Node(_name='foo'))
    assert not p(Node(_name='bar'))
    assert not p(Node(name='foo'))

    p = Name('foo', name_attr='name')
    assert p(Node(name='foo'))
    assert not p(Node(name='bar'))
    assert not p(Node(_name='foo'))

    p = Position(1)
    n = Node()
    with assign(n, POSITION, 0):
        assert not p(n)
    with assign(n, POSITION, 1):
        assert p(n)
    with assign(n, POSITION, 2):
        assert not p(n)

    p = Position(2, start_offset=1)
    n = Node()
    with assign(n, POSITION, 0):
        assert not p(n)
    with assign(n, POSITION, 1):
        assert p(n)
    with assign(n, POSITION, 2):
        assert not p(n)

#-------------------------------------------------------------------------------
# Functions

def test_functions():
    f = Function()
    assert_raises(NotImplementedError, f.eval, [])

    v = Value(1)
    assert v(Node()) == v.value == 1

    # --------------------Comparison--------------------

    f = Eq(1, 1)
    assert f._children == [Value(1), Value(1)]
    assert f(None)
    assert not Eq(1, 2)(None)

    assert Ne(1, 2)(None)
    assert not Ne(1, 1)(None)

    assert Lt(1, 2)(None)
    assert not Lt(1, 1)(None)

    assert Le(1, 2)(None)
    assert Le(1, 1)(None)
    assert not Le(1, 0)(None)

    assert Gt(2, 1)(None)
    assert not Gt(1, 1)(None)

    assert Ge(2, 1)(None)
    assert Ge(Identity(2), 1)(None)
    assert Ge(1, 1)(None)
    assert not Ge(0, 1)(None)

#-------------------------------------------------------------------------------
# Where

def test_where():
    n5 = Node(name = 'n5')
    n4 = Node(name = 'n4')
    n3 = Node(n4, name = 'n3')
    n2 = Node(name = 'n2')
    n1 = Node(n2, n3, n5, name = 'n1')

    def assign_name(n):
        n._name = n.name

    t = Tree(n1)
    t.depth_first(assign_name)

    q = Where(Child(), Name('n2')) # ./n2
    assert list(t.query(q)) == [n2]
    assert list(t.query(q, n3)) == []

    q = Where(Child(), Any()) # ./*
    assert list(t.query(q)) == [n2, n3, n5]
    assert list(t.query(q, n3)) == [n4]

    q = Where(Child(), Position(1)) #./[2]
    assert list(t.query(q)) == [n3]
    assert list(t.query(q, n3)) == []

    q = Where(Child(), Position(1, start_offset=1)) #./[1]
    assert list(t.query(q)) == [n2]
    assert list(t.query(q, n3)) == [n4]

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
