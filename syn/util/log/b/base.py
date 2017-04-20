from syn.tree.b import Node, Tree
from syn.base.b import Attr, init_hook

#-------------------------------------------------------------------------------
# Event


class Event(Node):
    def plaintext(self, **kwargs):
        cs = [c.plaintext(**kwargs) for c in self]
        return '\n'.join(cs)


#-------------------------------------------------------------------------------
# Logger


class Logger(Tree):
    _opts = dict(init_validate = True)
    _attrs = dict(root = Attr(Event),
                  current_parent = Attr(Event))

    @init_hook
    def _init(self):
        if type(self.root) is Node:
            self.root = Event()
        if not hasattr(self, 'current_parent'):
            self.current_parent = self.root

    def add(self, event):
        self.add_node(event, parent=self.current_parent)

    def plaintext(self, **kwargs):
        return self.root.plaintext(**kwargs)

    def pop(self):
        ret = self.current_parent
        self.current_parent = ret._parent
        return ret

    def push(self, event):
        self.add(event)
        self.current_parent = event

    def reset(self):
        self.current_parent = self.root


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Event', 'Logger')

#-------------------------------------------------------------------------------
