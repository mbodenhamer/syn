import ast
from copy import deepcopy
from functools import partial
from operator import itemgetter
from syn.base_utils import get_typename, ReflexiveDict, assign
from syn.tree.b import Node, Tree
from syn.base.b import create_hook, Attr, init_hook
from syn.type.a import TypeType, MultiType, Sequence
from syn.five import xrange

OAttr = partial(Attr, optional=True)

#-------------------------------------------------------------------------------

AST_REGISTRY = {}

#-------------------------------------------------------------------------------
# Group Names

AST = 'ast_attr'
ACO = 'ast_convert_attr'

#-------------------------------------------------------------------------------
# Custom Exceptions

class AstUnsupported(Exception):
    pass

class PythonError(Exception):
    pass

#-------------------------------------------------------------------------------
# Utilities

def is_expression_type(typ):
    if isinstance(typ, TypeType):
        return issubclass(typ.type, Expression)
    elif isinstance(typ, MultiType):
        return any(is_expression_type(t) for t in typ.types)
    elif isinstance(typ, Sequence):
        return is_expression_type(typ.item_type)
    raise PythonError('Should never query for: {}'.format(typ))

def resolve_progn(lst, **kwargs):
    out = []
    res = [item.resolve_progn(**kwargs) for item in lst]
    for item in res:
        if isinstance(item, ProgN):
            out.extend(item)
        else:
            out.append(item)
    return out

#-------------------------------------------------------------------------------
# Utility Classes

class NoAST(object):
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
                                        'per indent level'),
                  _children_set = Attr(bool, False, internal=True),
                  _child_map = Attr(dict, internal=True, init=lambda self: dict()))
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
        if key is not None and key is not NoAST:
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
        super(PythonNode, self)._init()

    def _set_children(self):
        self._children = []
        self._child_map = {}
        self._children_set = True
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

    def as_return(self, **kwargs):
        from .statements import Return
        return Return(self.copy())

    def as_value(self, **kwargs):
        '''Must return either an Expression or a ProgN.'''
        raise NotImplementedError

    def emit(self, **kwargs):
        raise NotImplementedError

    def expressify_statements(self, **kwargs):
        obj = self.copy()
        for attr in obj._groups[ACO]:
            typ = obj._attrs[attr].type
            if is_expression_type(typ):
                val = getattr(self, attr)
                if val is not None:
                    if isinstance(val, list):
                        res = [item.expressify_statements(**kwargs) 
                               for item in val]
                        res_ = [item if typ.item_type.query(item) else
                                item.as_value(**kwargs) for item in res]
                        setattr(obj, attr, res_)
                    else:
                        res = val.expressify_statements(**kwargs)
                        if not typ.query(res):
                            setattr(obj, attr, res.as_value(**kwargs))
        return obj

    @classmethod
    def from_ast(cls, ast, **kwargs):
        return cls(**kwargs)

    def resolve_progn(self, **kwargs):
        progns = []
        obj = self.copy()
        excludes = []
        if 'attr_exclude' in kwargs:
            excludes = kwargs['attr_exclude']
            del kwargs['attr_exclude']
        for attr in obj._groups[ACO]:
            if attr in excludes:
                continue
            val = getattr(obj, attr)
            if val is not None:
                if isinstance(val, list):
                    res = [item.resolve_progn(**kwargs) for item in val]
                    for k in xrange(len(res)):
                        item = res[k]
                        if isinstance(item, ProgN):
                            res[k] = item.value(**kwargs)
                            progns.append(item)
                    setattr(obj, attr, res)
                else:
                    res = val.resolve_progn(**kwargs)
                    if isinstance(res, ProgN):
                        setattr(obj, attr, res.value(**kwargs))
                        progns.append(res)
                    else:
                        setattr(obj, attr, res)

        if progns:
            ret = progns[0]
            for progn in progns[1:]:
                ret.extend(progn)
            ret.append(obj)
            return ret
        return obj

    def to_ast(self, **kwargs):
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(**kwargs_)

    def validate(self):
        if self._children_set:
            with assign(self, '_children', []):
                super(PythonNode, self).validate()
        else:
            super(PythonNode, self).validate()
            

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

    def expressify_statements(self, **kwargs):
        ret = self.copy()
        ret._children = [item.expressify_statements(**kwargs) for item in ret]
        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        cs = [from_ast(obj, **kwargs) for obj in ast.body]
        ret = cls(*cs)
        return ret

    def resolve_progn(self, **kwargs):
        ret = self.copy()
        ret._children = resolve_progn(ret, **kwargs)
        ret._init()
        return ret

    def to_ast(self, **kwargs):
        cs = [c.to_ast(**kwargs) for c in self]
        kwargs_ = self._to_ast_kwargs(**kwargs)
        return self.ast(cs, **kwargs_)


class Module(RootNode):
    pass


class Expression_(RootNode):
    ast = ast.Expression
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
# Base Classes


class Expression(PythonNode):
    _opts = dict(max_len = 0)
    ast = NoAST

    def as_value(self, **kwargs):
        return self.copy()


class Statement(PythonNode):
    _opts = dict(max_len = 0)


#-------------------------------------------------------------------------------
# Special


class Special(PythonNode):
    def validate(self):
        raise PythonError('Cannot exist in transformed PythonNode tree')


class ProgN(Special):
    def expressify_statements(self, **kwargs):
        raise NotImplementedError

    def resolve_progn(self, **kwargs):
        ret = self.copy()
        ret._children = resolve_progn(ret, **kwargs)
        ret._init()
        return ret

    def value(self, **kwargs):
        from .statements import Assign
        for child in reversed(self._children):
            if isinstance(child, Assign):
                return child.targets[0]
            if isinstance(child, ProgN):
                return child.value(**kwargs)
        else:
            raise PythonError('No value found')


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

__all__ = ('PythonNode', 'PythonTree', 'AstUnsupported', 'PythonError',
           'Context', 'Load', 'Store', 'Del', 'Param',
           'RootNode', 'Module', 'Expression_', 'Interactive', 
           'Special', 'ProgN', 'NoAST', 'Expression', 'Statement',
           'from_ast', 'from_source')

#-------------------------------------------------------------------------------
