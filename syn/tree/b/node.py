from functools import partial
from syn.five import STR
from syn.type.a import This
from syn.base.b import Base, ListWrapper, Attr, init_hook, setstate_hook
from syn.base_utils import last

#-------------------------------------------------------------------------------
# Utilities

IAttr = partial(Attr, internal=True)

EQEX = Base.groups_enum().eq_exclude
GSEX = Base.groups_enum().getstate_exclude
REPREX = Base.groups_enum().repr_exclude
STREX = Base.groups_enum().str_exclude

true = lambda x: True
identity = lambda x: x

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
        self._node_count += node.node_count()
        node._parent = self

    def remove_child(self, node):
        if node not in self._children:
            raise TreeError("Node '%s' not a child; cannot remove" % str(node))

        self._children.remove(node)
        self._node_count -= node.node_count()
        node._parent = None

    def parent(self):
        return self._parent

    def children(self):
        for c in self._children:
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

    def depth_first(self, func=identity, filt=true):
        if filt(self):
            yield func(self)

        for c in self._children:
            for x in c.depth_first(func, filt):
                yield x

    def rootward(self, func=identity, filt=true):
        if filt(self):
            yield func(self)

        if self._parent is not None:
            for x in self._parent.rootward(func, filt):
                yield x

    def ancestors(self, include_self=False):
        filt = true
        if not include_self:
            filt = lambda n: n != self

        for node in self.rootward(filt=filt):
            yield node

    def descendants(self, include_self=False):
        filt = true
        if not include_self:
            filt = lambda n: n != self

        for node in self.depth_first(filt=filt):
            yield node

    def attributes(self):
        for attr, spec in self._attrs.items():
            if not spec.internal:
                yield attr, getattr(self, attr)

    def root(self):
        return last(self.rootward())

    def siblings(self, preceding=False, following=False):
        if self._parent is not None:
            idx = self._parent._children.index(self)
            for k, c in enumerate(self._parent.children()):
                if c is not self:
                    if preceding:
                        if k < idx:
                            yield c
                    elif following:
                        if k > idx:
                            yield c
                    else:
                        yield c

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
