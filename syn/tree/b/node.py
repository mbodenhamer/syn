from functools import partial
from syn.five import STR
from syn.type.a import This
from syn.base.b import Base, ListWrapper, Attr, init_hook, setstate_hook

#-------------------------------------------------------------------------------
# Utilities

IAttr = partial(Attr, internal=True)

EQEX = Base.groups_enum().eq_exclude
GSEX = Base.groups_enum().getstate_exclude
REPREX = Base.groups_enum().repr_exclude
STREX = Base.groups_enum().str_exclude

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
                                doc='Child nodes')
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

    def remove_child(self, node):
        if node not in self._children:
            raise TreeError("Node '%s' not a child; cannot remove" % str(node))

        self._children.remove(node)
        node._parent = None

    def get_parent(self):
        return self._parent

    def get_children(self):
        return self._children

    def get_id(self):
        return self._id

    def get_name(self):
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

    def descendants(self, **kwargs):
        ret = self.collect_nodes()[1:]
        return ret

    def siblings(self, **kwargs):
        if self._parent is None:
            return []
        ret = [c for c in self._parent if c is not self]
        return ret

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
        return len(self.collect_nodes())

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
