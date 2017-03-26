import ast
from functools import partial
from syn.base_utils import setitem, pyversion
from syn.type.a import List
from syn.five import STR, xrange
from .base import PythonNode, Attr, AST, ACO
from .literals import Tuple, List as List_
from .variables import Name

VER = pyversion()
OAttr = partial(Attr, optional=True)

#-------------------------------------------------------------------------------
# Block


class Block(PythonNode):
    _attrs = dict(body = Attr(List(PythonNode), groups=(AST, ACO)))
    _opts = dict(max_len = 0)

    def emit_block(self, head, body, **kwargs):
        ret = self._indent(**kwargs)
        ret += head + ':\n'

        level = kwargs.get('indent_level', 0)
        with setitem(kwargs, 'indent_level', level + 1):
            strs = [elem.emit(**kwargs) for elem in body]

        ret += '\n'.join(strs)
        return ret


#-------------------------------------------------------------------------------
# If


class If(Block):
    _attrs = dict(test = Attr(PythonNode, groups=(AST, ACO)),
                  orelse = Attr(List(PythonNode), groups=(AST, ACO)))
    _opts = dict(args = ('test', 'body', 'orelse'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            head = 'if ' + self.test.emit(**kwargs)

        ret = self.emit_block(head, self.body, **kwargs)
        
        if self.orelse:
            head = 'else'
            block = self.emit_block(head, self.orelse, **kwargs)
            ret += '\n' + block

        return ret


#-------------------------------------------------------------------------------
# For


class For(Block):
    _attrs = dict(target = Attr((Name, Tuple, List_), groups=(AST, ACO)),
                  iter = Attr(PythonNode, groups=(AST, ACO)),
                  orelse = Attr(List(PythonNode), groups=(AST, ACO)))
    _opts = dict(args = ('target', 'iter', 'body', 'orelse'))
    
    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            head = 'for {} in {}'.format(self.target.emit(**kwargs),
                                         self.iter.emit(**kwargs))

        ret = self.emit_block(head, self.body, **kwargs)
        
        if self.orelse:
            head = 'else'
            block = self.emit_block(head, self.orelse, **kwargs)
            ret += '\n' + block

        return ret


#-------------------------------------------------------------------------------
# While


class While(Block):
    _attrs = dict(test = Attr(PythonNode, groups=(AST, ACO)),
                  orelse = Attr(List(PythonNode), groups=(AST, ACO)))
    _opts = dict(args = ('test', 'body', 'orelse'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            head = 'while ' + self.test.emit(**kwargs)

        ret = self.emit_block(head, self.body, **kwargs)
        
        if self.orelse:
            head = 'else'
            block = self.emit_block(head, self.orelse, **kwargs)
            ret += '\n' + block

        return ret


#-------------------------------------------------------------------------------
# Arguments


class Arguments(PythonNode):
    ast = ast.arguments
    _opts = dict(max_len = 0)
    _attrs = dict(args = Attr(List(Name), groups=(AST, ACO)),
                  vararg = Attr(STR, group=AST),
                  kwarg = Attr(STR, group=AST),
                  defaults = Attr(List(PythonNode), groups=(AST, ACO)))

    def emit2(self, **kwargs):
        with setitem(kwargs, 'indent_level', 0):
            n_defs = len(self.defaults)
            N = len(self.args) - n_defs
            strs = [self.args[k].emit(**kwargs) for k in xrange(N)]
            strs += ['{}={}'.format(self.args[k + N].emit(**kwargs),
                                    self.defaults[k].emit(**kwargs))
                     for k in xrange(n_defs)]
            if self.vararg:
                strs.append('*' + self.vararg)
            if self.kwarg:
                strs.append('**' + self.kwarg)

        return ', '.join(strs)

    def emit3(self, **kwargs):
        pass

    def emit(self, **kwargs):
        if VER >= '3':
            return self.emit3(**kwargs)
        return self.emit2(**kwargs)


#-------------------------------------------------------------------------------
# FunctionDef


class FunctionDef(Block):
    _attrs = dict(name = Attr(STR, group=AST),
                  args = Attr(Arguments, groups=(AST, ACO)),
                  decorator_list = OAttr(List(PythonNode), groups=(AST, ACO)))

    def emit_decorators(self, **kwargs):
        if not self.decorator_list:
            return ''

        pre = self._indent(**kwargs)
        with setitem(kwargs, 'indent_level', 0):
            strs = [pre + '@' + dec.emit(**kwargs) 
                    for dec in self.decorator_list]
        return '\n'.join(strs) + '\n'
        
    def emit(self, **kwargs):
        ret = self.emit_decorators(**kwargs)
        head = 'def ' + self.name + '(' + self.args.emit(**kwargs) + ')'
        ret += self.emit_block(head, self.body, **kwargs)
        return ret


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Block',
           'If', 'For', 'While',
           'Arguments', 'FunctionDef')

#-------------------------------------------------------------------------------
