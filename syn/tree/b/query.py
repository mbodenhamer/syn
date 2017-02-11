from __future__ import division
from operator import itemgetter
import operator as op
from syn.five import STR
from syn.type.a import Type as Type_
from syn.type.a import AnyType
from syn.base.b import Attr, init_hook, create_hook
from syn.base_utils import assign
from .node import Node

POSITION = '_nodeset_position'

#-------------------------------------------------------------------------------
# Query


class Query(Node):
    _opts = dict(max_len = 1)

    def __call__(self, node, **kwargs):
        if not self._children:
            for x in self.iterate(node):
                yield x
        
        else:
            for c in self.children():
                for n in c(node, **kwargs):
                    for x in self.iterate(n, **kwargs):
                        yield x

    def iterate(self, node, **kwargs):
        if False:
            yield # pragma: no cover


#-------------------------------------------------------------------------------
# Type


class Type(Query):
    _attrs = dict(type = Attr(Type_, AnyType()))
    _opts = dict(args = ('type',))

    @init_hook
    def _dispatch_type(self):
        if not isinstance(self.type, Type_):
            self.type = Type_.dispatch(self.type)

    def iterate(self, node, **kwargs):
        if self.type.query(node):
            yield node


#-------------------------------------------------------------------------------
# Axes


class Axis(Query):
    pass


#-----------------------------------------------------------
# Ancestor


class Ancestor(Axis):
    _attrs = dict(include_self = Attr(bool, False))

    def iterate(self, node, **kwargs):
        for k, a in enumerate(node.ancestors(include_self=self.include_self)):
            with assign(a, POSITION, k):
                yield a


#-----------------------------------------------------------
# Attribute

# TODO: return an Attr_ object instead (that can receive a position attr)
class Attribute(Axis):
    def iterate(self, node, **kwargs):
        for attr, value in node.attributes():
            yield attr, value


#-----------------------------------------------------------
# Child


class Child(Axis):
    def iterate(self, node, **kwargs):
        for k, c in enumerate(node.children()):
            with assign(c, POSITION, k):
                yield c


#-----------------------------------------------------------
# Descendant


class Descendant(Axis):
    _attrs = dict(include_self = Attr(bool, False))

    def iterate(self, node, **kwargs):
        for k, d in enumerate(node.descendants(include_self=self.include_self)):
            with assign(d, POSITION, k):
                yield d


#-----------------------------------------------------------
# Following


class Following(Axis):
    _attrs = dict(include_self = Attr(bool, False))

    def iterate(self, node, **kwargs):
        for k, f in enumerate(node.following()):
            with assign(f, POSITION, k):
                yield f


#-----------------------------------------------------------
# Parent


class Parent(Axis):
    def iterate(self, node, **kwargs):
        parent = node.parent()
        if parent is not None:
            with assign(parent, POSITION, 0):
                yield parent


#-----------------------------------------------------------
# Preceding


class Preceding(Axis):
    _attrs = dict(include_self = Attr(bool, False))

    def iterate(self, node, **kwargs):
        for k, p in enumerate(node.preceding()):
            with assign(p, POSITION, k):
                yield p


#-----------------------------------------------------------
# Root


class Root(Axis):
    def iterate(self, node, **kwargs):
        root = node.root()
        with assign(root, POSITION, 0):
            yield root


#-----------------------------------------------------------
# Self


class Self(Axis):
    def iterate(self, node, **kwargs):
        with assign(node, POSITION, 0):
            yield node


#-----------------------------------------------------------
# Sibling


class Sibling(Axis):
    _attrs = dict(following = Attr(bool, False),
                  preceding = Attr(bool, False))
    _opts = dict(one_true = [('following', 'preceding')])

    def iterate(self, node, **kwargs):
        for k, s in enumerate(node.siblings(following=self.following, 
                                            preceding=self.preceding, 
                                            axis=True)):
            with assign(s, POSITION, k):
                yield s


#-------------------------------------------------------------------------------
# Predicates


class Predicate(Query):
    _opts = dict(max_len = 0)

    def __call__(self, node, **kwargs):
        return self.eval(node, **kwargs)

    def eval(self, node, **kwargs):
        raise NotImplementedError


#-----------------------------------------------------------
# Any


class Any(Predicate):
    def eval(self, node, **kwargs):
        return True


#-----------------------------------------------------------
# Position


class Position(Predicate):
    _attrs = dict(pos = Attr(int),
                  start_offset = Attr(int, 0),
                  pos_attr = Attr(STR, POSITION))
    _opts = dict(args = ('pos',))

    def eval(self, node, **kwargs):
        pos = getattr(node, self.pos_attr)
        return pos == (self.pos - self.start_offset)


#-----------------------------------------------------------
# Name


class Name(Predicate):
    _attrs = dict(name = Attr(STR),
                  name_attr = Attr(STR, '_name'))
    _opts = dict(args = ('name',))

    def eval(self, node, **kwargs):
        return getattr(node, self.name_attr) == self.name


#-------------------------------------------------------------------------------
# Value


class Value(Query):
    _attrs = dict(value = Attr(None))
    _opts = dict(max_len = 0,
                 args = ('value',))
    
    def __call__(self, node, **kwargs):
        return self.value


#-------------------------------------------------------------------------------
# Function


class Function(Query):
    arity = None
    func = None

    def __init__(self, *args, **kwargs):
        lst = []
        for arg in args:
            if not isinstance(arg, Query):
                lst.append(Value(arg))
            else:
                lst.append(arg)
        super(Function, self).__init__(*lst, **kwargs)

    @classmethod
    @create_hook
    def _set_lens(cls):
        if cls.arity is not None:
            cls._opts.min_len = cls.arity
            cls._opts.max_len = cls.arity

    def __call__(self, node, **kwargs):
        values = [c(node, **kwargs) for c in self.children()]
        return self.eval(values, **kwargs)

    def eval(self, values, **kwargs):
        if self.func is None:
            raise NotImplementedError
        return self.func(*values)


#-----------------------------------------------------------
# Comparison

class Identity(Function):
    arity = 1
    func = lambda self, x: x

class Comparison(Function):
    arity = 2

class Eq(Comparison):
    func = op.eq

class Ne(Comparison):
    func = op.ne

class Lt(Comparison):
    func = op.lt

class Le(Comparison):
    func = op.le

class Gt(Comparison):
    func = op.gt

class Ge(Comparison):
    func = op.ge

#-------------------------------------------------------------------------------
# Where


class Where(Query):
    node = property(itemgetter(0))
    cond = property(itemgetter(1))

    _opts = dict(min_len = 2,
                 max_len = 2)

    def __call__(self, node, **kwargs):
        for k, n in enumerate(self.node(node, **kwargs)):
            if self.cond(n, **kwargs) is True:
                with assign(n, POSITION, k):
                    yield n


#-------------------------------------------------------------------------------
