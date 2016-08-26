from syn.type.a import Type as Type_
from syn.type.a import AnyType
from syn.base.b import Attr, init_hook
from .node import Node

#-------------------------------------------------------------------------------
# Query


class Query(Node):
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


#-------------------------------------------------------------------------------
# Type


class Type(Node):
    _attrs = dict(type = Attr(Type_, AnyType()))

    @init_hook
    def _dispatch_type(self):
        if not isinstance(self.type, Type_):
            self.type = Type_.dispatch(self.type)


#-------------------------------------------------------------------------------
# Axes


class Axis(Query):
    def __call__(self, node):
        if not self._children:
            for x in self.iterate(node):
                yield x
        else:
            for c in self.children():
                for n in c(node):
                    for x in self.iterate(n):
                        yield x


#-----------------------------------------------------------
# Ancestor


class Ancestor(Axis):
    _attrs = dict(include_self = Attr(bool, False))

    def iterate(self, node):
        for a in node.ancestors(include_self=self.include_self):
            yield a


#-----------------------------------------------------------
# Attribute


class Attribute(Axis):
    def iterate(self, node):
        for attr, value in node.attributes():
            yield attr, value


#-----------------------------------------------------------
# Child


class Child(Axis):
    def iterate(self, node):
        for c in node.children():
            yield c


#-----------------------------------------------------------
# Descendant


class Descendant(Axis):
    _attrs = dict(include_self = Attr(bool, False))

    def iterate(self, node):
        for d in node.descendants(include_self=self.include_self):
            yield d


#-----------------------------------------------------------
# Parent


class Parent(Axis):
    def iterate(self, node):
        yield node.parent()


#-----------------------------------------------------------
# Root


class Root(Axis):
    def iterate(self, node):
        yield node.root()


#-----------------------------------------------------------
# Self


class Self(Axis):
    def iterate(self, node):
        yield node


#-----------------------------------------------------------
# Sibling


class Sibling(Axis):
    _attrs = dict(following = Attr(bool, False),
                  preceding = Attr(bool, False))
    _opts = dict(one_true = [('following', 'preceding')])

    def iterate(self, node):
        for d in node.siblings(following=self.following, 
                               preceding=self.preceding, 
                               axis=True):
            yield d


#-------------------------------------------------------------------------------
