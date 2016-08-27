from collections import Iterator
from functools import partial
from syn.five import STR
from syn.type.a import This
from syn.base.b import Base, ListWrapper, Attr, init_hook, setstate_hook
from syn.base_utils import last, implies, consume

#-------------------------------------------------------------------------------
# Utilities

IAttr = partial(Attr, internal=True)

EQEX = Base.groups_enum().eq_exclude
GSEX = Base.groups_enum().getstate_exclude
REPREX = Base.groups_enum().repr_exclude
STREX = Base.groups_enum().str_exclude

true = lambda x: True
identity = lambda x: x

def _following_depth_first(node):
    for n in node.siblings(following=True):
        for x in n.depth_first():
            yield x

def _preceding_depth_first(node):
    for n in node.siblings(preceding=True, axis=True):
        for x in n.depth_first(reverse=True):
            yield x

    if node._parent is not None:
        yield node._parent

#-------------------------------------------------------------------------------
# TreeError

class TreeError(Exception): 
    pass

#-------------------------------------------------------------------------------
# Tree Node


class Node(ListWrapper):
    _attrs = dict(_parent = IAttr(This, optional=True,
                                  groups=(REPREX, STREX, EQEX, GSEX),
                                  doc='Parent of this node'),
                  _name = IAttr(STR, optional=True,
                                doc='Name of the node (for display purposes)'),
                  _id = IAttr(int, optional=True, doc='Integer id of the node'),
                  _list = IAttr(list, groups = (REPREX,),
                                doc='Child nodes'),
                  _node_count = IAttr(int, doc='The number of nodes in the subtree'
                                      'rooted by this node.')
                 )
    _aliases = dict(_list = ['_children'])
    _opts = dict(init_validate = False,
                 optional_none = True,
                 must_be_root = False)

    def __nonzero__(self):
        return True

    def __bool__(self):
        return True

    @init_hook
    def _initial_node_count(self):
        self._node_count = 1
        for c in self._children:
            self._node_count += c.node_count()

    @init_hook
    @setstate_hook
    def set_child_parents(self, parent=None, recurse=False):
        if parent is None:
            parent = self

        for c in self:
            c._parent = parent
            
            if recurse:
                c.set_child_parents(parent=parent, recurse=recurse)

    def add_child(self, node, index=None):
        if index is not None:
            self.insert(index, node)
        else:
            self.append(node)
        node._parent = self
        
        def adjust(n):
            n._node_count += node.node_count()
        consume(self.rootward(adjust))

    def remove_child(self, node):
        if node not in self._children:
            raise TreeError("Node '%s' not a child; cannot remove" % str(node))

        self._children.remove(node)
        node._parent = None

        def adjust(n):
            n._node_count -= node.node_count()
        consume(self.rootward(adjust))

    def parent(self):
        return self._parent

    def children(self, reverse=False):
        cs = self._children
        if reverse:
            cs = reversed(cs)

        for c in cs:
            yield c

    def id(self):
        return self._id

    def name(self):
        return self._name

    def collect_nodes(self, attr=None, val=None, key=None):
        nodes = []
        if attr is not None and val is not None:
            if getattr(self, attr) == val:
                nodes.append(self)
        elif key is not None:
            if not callable(key):
                raise TypeError('key must be callable: {}'.format(key))
            if key(self):
                nodes.append(self)
        else:
            nodes.append(self)

        for c in self:
            nodes.extend(c.collect_nodes(attr=attr, val=val, key=key))
        return nodes

    def collect_rootward(self, nodes=None):
        if nodes is None:
            nodes = []
        nodes.append(self)
        
        if self._parent is None:
            return nodes
        return self._parent.collect_rootward(nodes)

    def collect_by_type(self, typ):
        '''A more efficient way to collect nodes of a specified type than
        collect_nodes.
        '''
        nodes = []
        if isinstance(self, typ):
            nodes.append(self)
        for c in self:
            nodes.extend(c.collect_by_type(typ))
        return nodes

    def depth_first(self, func=identity, filt=true, reverse=False,
                    include_toplevel=True, top_level=True):
        if implies(top_level, include_toplevel):
            if filt(self):
                res = func(self)
                if not reverse:
                    yield res

        for c in self.children(reverse=reverse):
            for x in c.depth_first(func, filt, reverse, 
                                   include_toplevel, False):
                yield x

        if reverse:
            yield res

    def rootward(self, func=identity, filt=true, include_toplevel=True,
                 top_level=True):
        if implies(top_level, include_toplevel):
            if filt(self):
                res = func(self)
                if isinstance(res, Iterator):
                    for x in res:
                        yield x
                else:
                    yield res

        if self._parent is not None:
            for x in self._parent.rootward(func, filt, include_toplevel, False):
                yield x

    def attributes(self):
        for attr, spec in self._attrs.items():
            if not spec.internal:
                yield attr, getattr(self, attr)

    def ancestors(self, include_self=False):
        for node in self.rootward(include_toplevel=include_self):
            yield node

    def descendants(self, include_self=False):
        for node in self.depth_first(include_toplevel=include_self):
            yield node

    def following(self):
        for x in self.depth_first(include_toplevel=False):
            yield x
        
        for x in self.rootward(_following_depth_first):
            yield x

    def preceding(self):
        for x in self.rootward(_preceding_depth_first):
            yield x

    def siblings(self, preceding=False, following=False, axis=False):
        if self._parent is not None:
            idx = self._parent._children.index(self)

            reverse = False
            if axis and preceding:
                preceding = False
                following = True
                reverse = True
                idx = len(self._parent._children) - idx - 1

            for k, c in enumerate(self._parent.children(reverse=reverse)):
                if c is not self:
                    if following:
                        if k > idx:
                            yield c
                    elif preceding:
                        if k < idx:
                            yield c
                    else:
                        yield c

    def root(self):
        return last(self.rootward())

    def find_type(self, typ, children_only=False):
        # Search our current children first
        for c in self:
            if isinstance(c, typ):
                return c

        if not children_only:
            # If none of our children match, then search our descendants,
            # depth-first
            for c in self:
                ret = c.find_type(typ)
                if ret is not None:
                    return ret

        return None

    def node_count(self):
        return self._node_count

    def validate(self):
        super(Node, self).validate()

        if self._opts.must_be_root:
            if self._parent is not None:
                raise TreeError("node must be root, but has parent")

        for c in self:
            c.validate()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Node', 'TreeError')

#-------------------------------------------------------------------------------
