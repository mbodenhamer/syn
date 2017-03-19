import ast
from copy import deepcopy
from functools import partial
from operator import itemgetter
from syn.base_utils import get_typename, ReflexiveDict
from syn.tree.b import Node, Tree
from syn.base.b import create_hook, Attr

OAttr = partial(Attr, optional=True)

#-------------------------------------------------------------------------------

AST_REGISTRY = {}

#-------------------------------------------------------------------------------
# Group Names

AST = 'ast_attr'
ACO = 'ast_convert_attr'

#-------------------------------------------------------------------------------

class AstUnsupported(Exception):
    pass

#-------------------------------------------------------------------------------
# Base Class


class PythonNode(Node):
    ast = None
    minver = None
    maxver = None
    
    _attrs = dict(lineno = OAttr(int, group=AST),
                  col_offset = OAttr(int, group=AST))
    _opts = dict(optional_none = True)

    _groups = ReflexiveDict(AST, ACO)

    @classmethod
    @create_hook
    def _set_version(cls):
        if cls.minver is None:
            cls.minver = '0'
        if cls.maxver is None:
            cls.maxver = '100'
            
        cls.minver = str(cls.minver)
        cls.maxver = str(cls.maxver)

    @classmethod
    @create_hook
    def _register_ast(cls):
        if cls._class_data.dct.get('ast', None) is None:
            cls.ast = getattr(ast, get_typename(cls), None)

        key = cls.ast
        if key is not None:
            if key in AST_REGISTRY:
                raise TypeError("Class already registered for ast node '{}'"
                                 .format(key))
            AST_REGISTRY[key] = cls

    @classmethod
    def _from_ast_kwargs(cls, ast, **kwargs):
        vals = {}
        for attr in cls._groups[AST]:
            val = getattr(ast, attr, None)
            if attr in cls._groups[ACO]:
                val = from_ast(val, **kwargs)
            vals[attr] = val
        return vals

    def _to_ast_kwargs(self, **kwargs):
        ret = {}
        for attr in self._groups[AST]:
            val = getattr(self, attr, None)
            if val is not None:
                if attr in self._groups[ACO]:
                    val = val.to_ast(**kwargs)
                ret[attr] = val
        return ret

    def emit(self, **kwargs):
        cs = [c.emit(**kwargs) for c in self]
        return '\n'.join(cs)

    @classmethod
    def from_ast(cls, ast, **kwargs):
        cs = [from_ast(obj, **kwargs) for obj in ast.body]
        ret = cls(*cs)
        return ret

    def to_ast(self, **kwargs):
        cs = [c.to_ast(**kwargs) for c in self]
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(cs, **kwargs_)


#-------------------------------------------------------------------------------
# Contexts

class Context(PythonNode):
    _opts = dict(max_len = 0)

    @classmethod
    def from_ast(cls, ast, **kwargs):
        return cls()

    def to_ast(self, **kwargs):
        return self.ast()

class Load(Context):
    pass

class Store(Context):
    pass

class Del(Context):
    pass

#-------------------------------------------------------------------------------
# Root Nodes

class RootNode(PythonNode):
    pass

class Module(RootNode):
    pass

class Expression(RootNode):
    _opts = dict(min_len = 1,
                 max_len = 1)
    body = property(itemgetter(0))

    def emit(self, **kwargs):
        return self.body.emit(**kwargs)

    @classmethod
    def from_ast(cls, ast, **kwargs):
        child = from_ast(ast.body, **kwargs)
        ret = cls(child)
        return ret

    def to_ast(self, **kwargs):
        body = self.body.to_ast(**kwargs)
        return self.ast(body)

class Interactive(RootNode):
    pass

#-------------------------------------------------------------------------------
# PythonTree


class PythonTree(Tree):
    _opts = dict(init_validate = True)
    _attrs = dict(root = Attr(RootNode))

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
        raise AstUnsupported(get_typename(ast))
    kwargs.update(cls._from_ast_kwargs(ast, **kwargs))
    return cls.from_ast(ast, **kwargs)

def from_source(src, mode='exec'):
    tree = ast.parse(src, mode=mode)
    root = from_ast(tree)
    return PythonTree(root)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('PythonNode', 'PythonTree', 'AstUnsupported',
           'Context', 'Load', 'Store', 'Del',
           'RootNode', 'Module', 'Expression', 'Interactive',
           'from_ast', 'from_source')

#-------------------------------------------------------------------------------
