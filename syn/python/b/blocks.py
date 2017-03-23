from syn.base_utils import setitem
from syn.type.a import List
from .base import PythonNode, Attr, col_offset, AST, ACO
from .literals import Tuple, List as List_
from .variables import Name

#-------------------------------------------------------------------------------
# Block


class Block(PythonNode):
    _attrs = dict(body = Attr(List(PythonNode), groups=(AST, ACO)),
                  indent = Attr(int, 4))
    _opts = dict(max_len = 0)

    def emit_block(self, head, body, **kwargs):
        block_offset = col_offset(self, kwargs)
        ret = ' ' * block_offset
        ret += head + ':\n'

        # TODO: check if indent was explicitly set on init and if so
        # override with that value
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
    _attrs = dict(test = Attr(PythonNode, groups=(AST, ACO)),
                  orelse = Attr(List(PythonNode), groups=(AST, ACO)))
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


#-------------------------------------------------------------------------------
# For


class For(Block):
    _attrs = dict(target = Attr((Name, Tuple, List_), groups=(AST, ACO)),
                  iter = Attr(PythonNode, groups=(AST, ACO)),
                  orelse = Attr(List(PythonNode), groups=(AST, ACO)))
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


#-------------------------------------------------------------------------------
# While


class While(Block):
    _attrs = dict(test = Attr(PythonNode, groups=(AST, ACO)),
                  orelse = Attr(List(PythonNode), groups=(AST, ACO)))
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


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Block',
           'If', 'For', 'While')

#-------------------------------------------------------------------------------
