from syn.python.b import Module
from .base import SyntagmathonNode

#-------------------------------------------------------------------------------
# Module API

def _to_python_native(obj, **kwargs):
    from syn.python.b import Num
    
    if Num._attrs.types['n'].query(obj):
        return Num(obj)
    raise TypeError("Cannot compile: {}".format(obj))

def to_python(obj, **kwargs):
    if not isinstance(obj, SyntagmathonNode):
        if isinstance(obj, list):
            return [to_python(item, **kwargs) for item in obj]
        elif isinstance(obj, tuple):
            if not obj:
                from syn.python.b import Call, Name
                return Call(Name('list'))
            func = obj[0]
            args = obj[1:]
            return to_python(func(*args), **kwargs)
        return _to_python_native(obj, **kwargs)
    return obj.to_python(**kwargs)

def compile_to_python(obj, **kwargs):
    py = to_python(obj, **kwargs)
    if isinstance(py, list):
        py = Module(*py)
    out = py.expressify_statements().resolve_progn()
    out.validate()
    return out.emit(**kwargs)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('to_python', 'compile_to_python')

#-------------------------------------------------------------------------------
