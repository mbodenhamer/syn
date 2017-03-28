from .base import SyntagmathonNode
from .interpreter import Env

#-------------------------------------------------------------------------------
# Module API

def _to_python_native(obj, **kwargs):
    from syn.python.b import Num
    
    if Num._attrs.types['n'].check(obj):
        return Num(obj)
    raise TypeError("Cannot compile: {}".format(obj))

def to_python(obj, env=None, **kwargs):
    if env is None:
        env = Env()

    if not isinstance(obj, SyntagmathonNode):
        if isinstance(obj, list):
            return [to_python(item, env, **kwargs) for item in obj]
        return _to_python_native(obj, **kwargs)
    return obj.to_python(env, **kwargs)

def compile_to_python(obj, **kwargs):
    py = to_python(obj, **kwargs)
    return py.emit(**kwargs)

#-------------------------------------------------------------------------------
# __all__

__all__ = ('to_python', 'compile_to_python')

#-------------------------------------------------------------------------------
