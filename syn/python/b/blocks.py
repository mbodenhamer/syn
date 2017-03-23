from syn.base_utils import setitem
from syn.type.a import List
from .base import PythonNode, Attr, AST, ACO
from .literals import Tuple, List as List_
from .variables import Name

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
# __all__

__all__ = ('Block',
           'If', 'For', 'While')

#-------------------------------------------------------------------------------
