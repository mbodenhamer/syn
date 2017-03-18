import ast
from copy import deepcopy
from syn.base_utils import get_typename
from syn.tree.b import Node, Tree
from syn.base.b import create_hook, Attr

#-------------------------------------------------------------------------------

AST_REGISTRY = {}

#-------------------------------------------------------------------------------

class ASTUnsupported(Exception):
    pass

#-------------------------------------------------------------------------------
# Base Class


class PythonNode(Node):
    ast = None
    minver = None
    maxver = None
    
    @classmethod
    @create_hook
    def _register_ast(cls):
        key = cls.ast
        if key is not None:
            if key in AST_REGISTRY:
                raise TypeError("Class already registered for ast node '{}'"
                                 .format(key))
            AST_REGISTRY[key] = cls

    def emit(self, args):
        raise NotImplementedError()

    @classmethod
    def from_ast(cls, ast, **kwargs):
        raise NotImplementedError()

    def to_ast(self, args):
        raise NotImplementedError()


#-------------------------------------------------------------------------------
# PythonTree


class PythonTree(Tree):
    _opts = dict(init_validate = True)
    _attrs = dict(root = Attr(PythonNode))

    def abstract(self):
        def op(node):
            node.lineno = None
            node.col_offset = None

        ret = deepcopy(self)
        ret.depth_first(op)
        return ret

    def emit(self, **kwargs):
        return self.root.emit(**kwargs)

    def to_ast(self, **kwargs):
        return self.root.to_ast(**kwargs)


#-------------------------------------------------------------------------------
# Module API

def from_ast(ast, **kwargs):
    try:
        cls = AST_REGISTRY[type(ast)]
    except KeyError:
        raise ASTUnsupported(get_typename(ast))
    return cls.from_ast(ast, **kwargs)

def from_source(src, mode='exec'):
    tree = ast.parse(src, mode=mode)
    root = from_ast(tree)
    return PythonTree(root)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('PythonNode', 'PythonTree',
           'from_ast', 'from_source')

#-------------------------------------------------------------------------------
