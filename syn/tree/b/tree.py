from syn.five import STR
from syn.type.a import List, Dict
from syn.base.b import Base, Attr, Counter
from .node import Node, TreeError
from syn.base_utils import get_typename, getitem

#-------------------------------------------------------------------------------
# Default search functions

def do_nothing(*args, **kwargs):
    pass

def identity(x):
    return x

#-------------------------------------------------------------------------------
# Tree


class Tree(Base):
    _attrs = dict(root = Attr(Node, init=lambda self: Node(),
                              doc="The root node of the tree"),
                  nodes = Attr(List(Node), init=lambda self: list(),
                               doc="List of all tree nodes"),
                  node_types = Attr(List(STR), init=lambda self: list(),
                                    doc="List of all tree node types"),
                  id_dict = Attr(Dict(Node), init=lambda self: dict(),
                                 doc="Mapping of ids to nodes"),
                  type_dict = Attr(Dict(List(Node)), init=lambda self: dict(),
                                   doc="Mapping of type names to node lists"),
                  node_counter = Attr(Counter, init=lambda self: Counter(),
                                      groups = ('eq_exclude',),
                                      doc='Node id counter'),
                 )
    _opts = dict(init_validate = True,
                 args = ('root',))

    def __init__(self, *args, **kwargs):
        super(Tree, self).__init__(*args, **kwargs)
        self.add_node(self.root)

    def add_node(self, node, **kwargs):
        if node in self.nodes:
            raise TreeError("Node '{}' already in tree; cannot add"
                            .format(repr(node)))

        def add_node(_node):
            if _node._id is None:
                _node._id = self.node_counter()

            self.id_dict[_node._id] = _node
            self.nodes.append(_node)
            if get_typename(_node) not in self.node_types:
                self.node_types.append(get_typename(_node))
            if get_typename(_node) not in self.type_dict:
                self.type_dict[get_typename(_node)] = []
            self.type_dict[get_typename(_node)].append(_node)
            
        if node != self.root:
            parent = getitem(kwargs, 'parent', None, True)
            if not parent:
                parent = self.get_node_by_id(getitem(kwargs, 'parent_id',
                                                     max(self.id_dict)))

            if parent not in self.nodes:
                raise TreeError("Parent node '{}' not in tree" 
                                .format(repr(parent)))
            parent.add_child(node)

        self.depth_first(node=add_node, current_node=node)

    def remove_node(self, node, **kwargs):
        if node not in self.nodes:
            raise TreeError("Node '{}' not in tree; cannot remove" 
                            .format(repr(node)))

        def remove_node(_node):
            del self.id_dict[_node._id]
            self.nodes.remove(_node)
            self.type_dict[get_typename(_node)].remove(_node)
            if self.type_dict[get_typename(_node)] == []:
                self.node_types.remove(get_typename(_node))
                del self.type_dict[get_typename(_node)]

        if node != self.root:
            parent = node.get_parent()
            if parent is None:
                raise TreeError("Non-root node '{}' has no parent" 
                                .format(repr(node)))
            parent.remove_child(node)
        else:
            self.root = None

        self.depth_first(node=remove_node, current_node=node)

    def replace_node(self, source, dest, **kwargs):
        if dest.get_parent() is not None:
            raise TreeError("Node dest must have no parent")

        parent = source.get_parent()
        if parent is None:
            if source == self.root:
                self.remove_node(source, **kwargs)
                self.root = dest
                self.add_node(dest, **kwargs)
            else:
                raise TreeError("Non-root node '{}' has no parent"
                                .format(repr(source)))
        else:
            self.remove_node(source, **kwargs)
            self.add_node(dest, parent=parent, **kwargs)

    def rebuild(self, **kwargs):
        '''Repopulate the node-tracking data structures.  Shouldn't
        really ever be needed.
        '''
        self.nodes = []
        self.node_types = []
        self.id_dict = {}
        self.type_dict = {}

        self.add_node(self.root)

    def get_node_by_id(self, node_id):
        ret = getitem(self.id_dict, node_id,
                      self._get_node_by_id(node_id), True)
        return ret

    def _get_node_by_id(self, node_id):
        for n in self.nodes:
            if n._id == node_id:
                return n
        return None

    def _check_search_kwarg_types(self, kwargs):
        '''Checks that every element of kwargs is a valid type in this tree.'''
        for key in kwargs:
            if key not in self.node_types:
                raise TypeError("Invalid search type: {}".format(key))

    def depth_first(self, node = do_nothing,
                    stop_test = do_nothing,
                    _return = identity,
                    current_node = 'root',
                    **kwargs):

        self._check_search_kwarg_types(kwargs)
        if current_node == 'root':
            current_node = self.root

        node(current_node)
        if stop_test(current_node):
            return _return(current_node)

        for nodetype, function in kwargs.items():
            if get_typename(current_node) == nodetype:
                function(current_node)
                
        for child in current_node.get_children():
            ret = self.depth_first(node, stop_test, _return, child, **kwargs)
            if ret:
                return ret

    def search_rootward(self, node = do_nothing,
                        stop_test = do_nothing,
                        _return = identity,
                        current_node = 'root',
                        **kwargs):
        
        self._check_search_kwarg_types(kwargs)
        
        if current_node == 'root':
            current_node = self.root

        node(current_node)
        if stop_test(current_node):
            return _return(current_node)

        for nodetype, function in kwargs.items():
            if get_typename(current_node) == nodetype:
                function(current_node)

        if current_node is self.root:
            return

        parent = current_node.get_parent()
        return self.search_rootward(node, stop_test, _return, parent, **kwargs)

    def validate(self):
        super(Tree, self).validate()
        self.root.validate()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Tree', 'do_nothing', 'identity')

#-------------------------------------------------------------------------------
