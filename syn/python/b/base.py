import ast
from copy import deepcopy
from functools import partial
from operator import itemgetter
from syn.base_utils import get_typename, ReflexiveDict, AttrDict
from syn.tree.b import Node, Tree
from syn.base.b import create_hook, Attr, init_hook

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
                  col_offset = OAttr(int, group=AST),
                  indent_amount = OAttr(int, 4, 'The number of spaces to indent '
                                        'per indent level'))
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
                if isinstance(val, list):
                    val = [from_ast(v, **kwargs) if v is not None else None
                           for v in val]
                elif val is not None:
                    val = from_ast(val, **kwargs)
            vals[attr] = val
        return vals

    @init_hook
    def _init(self):
        if not self._children:
            self._set_children()

    def _set_children(self):
        self._children = []
        for attr in self._groups[ACO]:
            val = getattr(self, attr)
            if val is not None:
                if isinstance(val, list):
                    for item in val:
                        if item is not None:
                            self._children.append(item)
                            item._parent = self
                else:
                    val._parent = self
                    self._children.append(val)

        # max_len and min_len allow for specifying positional args
        # since the object has been initialized, set to avoid validation errors
        self._opts = AttrDict(self._opts)
        self._opts.max_len = len(self)
        self._opts.min_len = len(self)

    def _indent(self, **kwargs):
        level = kwargs.get('indent_level', 0)
        n = self.indent_amount * level
        return ' ' * n

    def _to_ast_kwargs(self, **kwargs):
        ret = {}
        for attr in self._groups[AST]:
            val = getattr(self, attr, None)
            if val is not None:
                if attr in self._groups[ACO]:
                    if isinstance(val, list):
                        val = [v.to_ast(**kwargs) if v is not None else None
                               for v in val]
                    elif val is not None:
                        val = val.to_ast(**kwargs)
                ret[attr] = val
        return ret

    def add_return(self, **kwargs):
        from .statements import Return
        return Return(self)

    def emit(self, **kwargs):
        raise NotImplementedError

    @classmethod
    def from_ast(cls, ast, **kwargs):
        return cls(**kwargs)

    def to_ast(self, **kwargs):
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(**kwargs_)

    def transform(self, **kwargs):
        pass


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


class Param(Context):
    maxver = '2.9999999999'


#-------------------------------------------------------------------------------
# Root Nodes


class RootNode(PythonNode):
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
# Special

#-------------------------------------------------------------------------------
# PythonTree


class PythonTree(Tree):
    _opts = dict(init_validate = True)
    _attrs = dict(root = Attr(RootNode))

    def abstract(self):
        def op(node):
            node.lineno = None

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
           'Context', 'Load', 'Store', 'Del', 'Param',
           'RootNode', 'Module', 'Expression', 'Interactive',
           'from_ast', 'from_source')

#-------------------------------------------------------------------------------
