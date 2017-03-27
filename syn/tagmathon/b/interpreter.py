from syn.base.b import Base, Attr
from syn.type.a import List
from .base import SyntagmathonNode

#-------------------------------------------------------------------------------
# Frame


class Frame(Base):
    _attrs = dict(globals = Attr(dict, init=lambda self: dict()),
                  locals = Attr(dict, init=lambda self: dict()))
    _opts = dict(init_validate = True)

    def __getitem__(self, key):
        if key in self.locals:
            return self.locals[key]
        elif key in self.globals:
            return self.globals[key]
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.locals[key] = value

    def __delitem__(self, key):
        if key in self.locals:
            del self.locals[key]
        elif key in self.globals:
            del self.globals[key]
        else:
            raise KeyError(key)

    def __iter__(self):
        return iter(sorted(set(self.locals) | set(self.globals)))

    def __len__(self):
        return len(set(self.locals) | set(self.globals))

    def items(self):
        for key in self:
            yield key, self[key]

    def gensym(self):
        pass

    def set_global(self, key, value):
        self.globals[key] = value
        
    def update(self, dct):
        for key, value in dct.items():
            self[key] = value


#-------------------------------------------------------------------------------
# Env


class Env(Base):
    _attrs = dict(frames = Attr(List(Frame), init=lambda self: list([Frame()])))
    _opts = dict(init_validate = True)

    current_frame = property(lambda self: self.frames[-1])

    def __getitem__(self, key):
        return self.current_frame[key]

    def __setitem__(self, key, value):
        self.current_frame[key] = value

    def __delitem__(self, key):
        del self.current_frame[key]

    def __iter__(self):
        return iter(self.current_frame)

    def __len__(self):
        return len(self.current_frame)

    def items(self):
        for item in self.current_frame.items():
            yield item

    def gensym(self):
        pass

    def globals(self):
        return dict(self.current_frame.globals)

    def locals(self):
        return dict(self.current_frame.locals)

    def push(self, dct):
        globs = self.globals()
        globs.update(self.locals())
        self.frames.append(Frame(globals=globs, locals=dct))

    def pop(self):
        return self.frames.pop()
        
    def set_global(self, key, value):
        self.current_frame.set_global(key, value)

    def update(self, dct):
        self.current_frame.update(dct)


#-------------------------------------------------------------------------------
# Module API

def eval(obj, env=None, **kwargs):
    if env is None:
        env = Env()

    if not isinstance(obj, SyntagmathonNode):
        if isinstance(obj, list):
            return [eval(item, env, **kwargs) for item in obj][-1]
        return obj
    return obj.eval(env, **kwargs)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('Frame', 'Env', 'eval')

#-------------------------------------------------------------------------------
