import ast
from copy import deepcopy
from operator import itemgetter
from functools import partial, wraps
from syn.base_utils import get_typename, ReflexiveDict, assign
from syn.util.log.b import StringEvent
from syn.tree.b import Node, Tree
from syn.base.b import create_hook, Attr, init_hook, Base, Counter
from syn.type.a import TypeType, MultiType, Sequence
from syn.types.a import attrs

OAttr = partial(Attr, optional=True)

#-------------------------------------------------------------------------------
# Registry

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
# Custom Logging Events

class TransformEvent(StringEvent):
    _attrs = dict(obj = Attr(object),
                  ret = Attr(object, optional=True))
    _opts = dict(optional_none = True)

    def display(self, depth=None):
        pre = ' ' * depth
        ret = pre + self._plaintext() + ' ({})\n'.format(self._id)
        if self.obj:
            ret += self.obj.viewable().pretty(indent=depth)
        if self.ret:
            ret += '\n'
            ret += self.ret.viewable().pretty(indent=depth)
        return ret

class AsValue(TransformEvent):
    pass

class Expressify(TransformEvent):
    pass

class ResolveProgN(TransformEvent):
    pass

class ProgNValue(TransformEvent):
    pass

class ProgNValuify(TransformEvent):
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

class logging(object):
    def __init__(self, event_type, push=True):
        self.event_type = event_type
        self.push = push

    def __call__(self, f):
        @wraps(f)
        def func(obj, *args, **kwargs):
            logger = kwargs.get('logger', None)
            if logger:
                event = self.event_type(s=get_typename(obj), obj=obj)
                if self.push:
                    logger.push(event)
                else:
                    logger.add(event)
            ret = f(obj, *args, **kwargs)
            if logger:
                event.ret = ret
                if self.push:
                    logger.pop()
            return ret
        return func

#-------------------------------------------------------------------------------
# Utility Classes


class NoAST(object):
    '''Dummy class to prevent binding to a specific ast object.'''


class GenSym(Base):
    _attrs = dict(names = Attr(set, init=lambda self: set()),
                  counter = Attr(Counter, init=lambda self: Counter()))
    _opts = dict(args = ('names',),
                 init_validate = True)

    def add(self, name):
        self.names.add(name)

    def _generate(self):
        return '_gensym_{}'.format(self.counter())

    def generate(self):
        ret = self._generate()
        while ret in self.names:
            ret = self._generate()
        self.add(ret)
        return ret

    def update(self, names):
        self.names.update(names)


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
                  _child_map = Attr(dict, internal=True, init=lambda self: dict()),
                  _progn_value = OAttr(object, internal=True))
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
    
    def _child_attr(self, k):
        spec = self._child_map[k]
        if isinstance(spec, tuple):
            return spec[0]
        return spec

    def _child_attr_type(self, k):
        return self._attrs[self._child_attr(k)].type 

    def _child_type_query(self, k, value):
        typ = self._child_attr_type(k)
        if isinstance(typ, Sequence):
            return typ.item_type.query(value)
        return typ.query(value)

    def _is_child_attr_expression_type(self, k):
        return is_expression_type(self._child_attr_type(k))

    def _set_children(self):
        k = 0
        self._children = []
        self._child_map = {}
        self._children_set = True
        for attr in self._groups[ACO]:
            val = getattr(self, attr)
            if val is not None:
                if isinstance(val, list):
                    for idx, item in enumerate(val):
                        if item is not None:
                            self._children.append(item)
                            item._parent = self
                            self._child_map[k] = (attr, idx)
                            k += 1
                else:
                    val._parent = self
                    self._children.append(val)
                    self._child_map[k] = attr
                    k += 1

    def _set_child(self, k, value):
        value._parent = self
        diff = value._node_count - self._children[k]._node_count
        self._children[k] = value
        self._node_count += diff

        spec = self._child_map[k]
        if isinstance(spec, tuple): # list element
            attr, idx = spec
            getattr(self, attr)[idx] = value
        else:
            setattr(self, spec, value)

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

    @logging(Expressify)
    def expressify_statements(self, **kwargs):
        if 'gensym' not in kwargs:
            kwargs['gensym'] = GenSym(self.variables(**kwargs))

        obj = self.copy()
        for k, val in enumerate(obj._children):
            if obj._is_child_attr_expression_type(k):
                if not obj._child_type_query(k, val):
                    res = val.expressify_statements(**kwargs)
                    if not obj._child_type_query(k, res):
                        res = res.as_value(**kwargs)
                    obj._set_child(k, res)

        return obj

    @classmethod
    def from_ast(cls, ast, **kwargs):
        return cls(**kwargs)

    @logging(ResolveProgN)
    def resolve_progn(self, **kwargs):
        if 'gensym' not in kwargs:
            kwargs['gensym'] = GenSym(self.variables(**kwargs))

        excludes = []
        if 'attr_exclude' in kwargs:
            excludes = kwargs['attr_exclude']
            del kwargs['attr_exclude']

        progns = []
        obj = self.copy()
        for k, val in enumerate(obj._children):
            if obj._child_attr(k) in excludes:
                continue

            res = val.resolve_progn(**kwargs)
            if isinstance(res, ProgN):
                res = res.valuify(**kwargs)
                progns.append(res)
                res = res.value(**kwargs)
            obj._set_child(k, res)

        if progns:
            ret = progns[0]
            for progn in progns[1:]:
                ret.extend(progn)
            ret.append(obj)
            ret._init()
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

    def variables(self, **kwargs):
        ret = set()
        for c in self._children:
            ret.update(c.variables(**kwargs))
        return ret

    def viewable(self, **kwargs):
        ret = self.copy()
        excludes = kwargs.get('excludes', ['lineno', 'col_offset', 'ctx'])

        if ret._children_set:
            for k, val in enumerate(ret._children):
                ret._set_child(k, val.viewable(**kwargs))
            ret._children = []
        else:
            ret._children = [c.viewable(**kwargs) for c in ret]

        excl = ret._groups['str_exclude']
        excl.update(excludes)
        for attr in attrs(ret):
            if attr not in ret._groups[AST]:
                excl.add(attr)
        
        ret._groups['str_exclude'] = excl
        return ret


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

    @logging(Expressify)
    def expressify_statements(self, **kwargs):
        ret = self.copy()
        ret._children = [item.expressify_statements(**kwargs) for item in ret]
        ret._init()
        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        cs = [from_ast(obj, **kwargs) for obj in ast.body]
        ret = cls(*cs)
        return ret

    @logging(ResolveProgN)
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

    @logging(AsValue, push=False)
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

    @logging(ResolveProgN)
    def resolve_progn(self, **kwargs):
        ret = self.copy()
        ret._children = resolve_progn(ret, **kwargs)
        ret._init()
        return ret

    @logging(ProgNValue)
    def value(self, **kwargs):
        if not self._children:
            raise PythonError('No value found')

        child = self[-1]
        from .statements import Assign
        if isinstance(child, Assign):
            return child.targets[0]

        if isinstance(child, ProgN):
            return child.value(**kwargs)

        if child._progn_value is not None:
            return child._progn_value

        raise PythonError('No value found')

    @logging(ProgNValuify)
    def _valuify(self, **kwargs):
        if not self._children:
            raise PythonError('Cannot valuify empty ProgN')

        ret = self.copy()
        from .variables import Name
        from .statements import Assign

        if 'gensym' not in kwargs:
            kwargs['gensym'] = GenSym(ret.variables(**kwargs))
        name = Name(kwargs['gensym'].generate())
        
        child = ret[-1]
        if not isinstance(child, Expression):
            child = child.as_value(**kwargs).resolve_progn(**kwargs)

        ret[-1] = Assign([name], child)
        ret._init()
        return ret

    def valuify(self, **kwargs):
        try:
            self.value(**kwargs)
            return self
        except PythonError:
            return self._valuify(**kwargs)


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
