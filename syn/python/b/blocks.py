from syn.base_utils import setitem
from syn.type.a import List
from .base import PythonNode, Attr, from_ast, col_offset
from .literals import Tuple, List as List_
from .variables import Name

#-------------------------------------------------------------------------------
# Block


class Block(PythonNode):
    _attrs = dict(body = Attr(List(PythonNode)),
                  indent = Attr(int, 4))
    _opts = dict(max_len = 0)

    def emit_block(self, head, body, **kwargs):
        block_offset = col_offset(self, kwargs)
        ret = ' ' * block_offset
        ret += head + ':\n'

        body_offset = body[0].col_offset if body[0].col_offset is not None else 0
        body_offset = (body_offset if body_offset > block_offset else 
                       block_offset + self.indent)

        with setitem(kwargs, 'col_offset', body_offset):
            strs = [elem.emit(**kwargs) for elem in body]

        ret += '\n'.join(strs)
        return ret


#-------------------------------------------------------------------------------
# If


class If(Block):
    _attrs = dict(test = Attr(PythonNode),
                  orelse = Attr(List(PythonNode)))
    _opts = dict(args = ('test', 'body', 'orelse'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            head = 'if ' + self.test.emit(**kwargs)

        ret = self.emit_block(head, self.body, **kwargs)
        
        if self.orelse:
            head = 'else'
            block = self.emit_block(head, self.orelse, **kwargs)
            ret += '\n' + block

        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        test = from_ast(ast.test, **kwargs)
        body = [from_ast(elem, **kwargs) for elem in ast.body]
        orelse = [from_ast(elem, **kwargs) for elem in ast.orelse]
        return cls(test, body, orelse)

    def to_ast(self, **kwargs):
        test = self.test.to_ast(**kwargs)
        body = [elem.to_ast(**kwargs) for elem in self.body]
        orelse = [elem.to_ast(**kwargs) for elem in self.orelse]
        return self.ast(test, body, orelse)


#-------------------------------------------------------------------------------
# For


class For(Block):
    _attrs = dict(target = Attr((Name, Tuple, List_)),
                  iter = Attr(PythonNode),
                  orelse = Attr(List(PythonNode)))
    _opts = dict(args = ('target', 'iter', 'body', 'orelse'))
    
    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            head = 'for {} in {}'.format(self.target.emit(**kwargs),
                                         self.iter.emit(**kwargs))

        ret = self.emit_block(head, self.body, **kwargs)
        
        if self.orelse:
            head = 'else'
            block = self.emit_block(head, self.orelse, **kwargs)
            ret += '\n' + block

        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        target = from_ast(ast.target, **kwargs)
        iter = from_ast(ast.iter, **kwargs)
        body = [from_ast(elem, **kwargs) for elem in ast.body]
        orelse = [from_ast(elem, **kwargs) for elem in ast.orelse]
        return cls(target, iter, body, orelse)

    def to_ast(self, **kwargs):
        target = self.target.to_ast(**kwargs)
        iter = self.iter.to_ast(**kwargs)
        body = [elem.to_ast(**kwargs) for elem in self.body]
        orelse = [elem.to_ast(**kwargs) for elem in self.orelse]
        return self.ast(target, iter, body, orelse)


#-------------------------------------------------------------------------------
# While


class While(Block):
    _attrs = dict(test = Attr(PythonNode),
                  orelse = Attr(List(PythonNode)))
    _opts = dict(args = ('test', 'body', 'orelse'))

    def emit(self, **kwargs):
        with setitem(kwargs, 'col_offset', 0):
            head = 'while ' + self.test.emit(**kwargs)

        ret = self.emit_block(head, self.body, **kwargs)
        
        if self.orelse:
            head = 'else'
            block = self.emit_block(head, self.orelse, **kwargs)
            ret += '\n' + block

        return ret

    @classmethod
    def from_ast(cls, ast, **kwargs):
        test = from_ast(ast.test, **kwargs)
        body = [from_ast(elem, **kwargs) for elem in ast.body]
        orelse = [from_ast(elem, **kwargs) for elem in ast.orelse]
        return cls(test, body, orelse)

    def to_ast(self, **kwargs):
        test = self.test.to_ast(**kwargs)
        body = [elem.to_ast(**kwargs) for elem in self.body]
        orelse = [elem.to_ast(**kwargs) for elem in self.orelse]
        return self.ast(test, body, orelse)


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Block',
           'If', 'For', 'While')

#-------------------------------------------------------------------------------
