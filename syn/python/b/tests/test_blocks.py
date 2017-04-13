from nose.tools import assert_raises
from .test_statements import examine
from syn.python.b import Block, If, Num, Assign, Name, Return, Module
from syn.base_utils import pyversion

VER = pyversion()

#-------------------------------------------------------------------------------
# Block

def test_block():
    Block

#-------------------------------------------------------------------------------
# If

def test_if():
    examine('if 1:\n    a = 1')
    examine('if 1:\n    a = 1\nelse:\n    a = 2')
    examine('if 1:\n  a = 1\nelif 2:\n  a = 2\nelse:\n  a = 3',
            'if 1:\n    a = 1\nelse:\n    if 2:\n        a = 2\n    else:\n        a = 3')

    if1 = If(Num(1), [Num(2)], [Num(3)])
    assert if1.emit() == 'if 1:\n    2\nelse:\n    3'

    rif1 = if1.as_return()
    assert rif1.emit() == 'if 1:\n    return 2\nelse:\n    return 3'

    if2 = If(Assign([Name('x')], Num(2)),
             [Return(Num(5))])
    assert if2.emit() == 'if x = 2:\n    return 5'

#-------------------------------------------------------------------------------
# For

def test_for():
    examine('for x in [1, 2]:\n    a = x\n    b = y')
    examine('for x in (1, 2):\n    a = x\nelse:\n    b = x')

#-------------------------------------------------------------------------------
# While

def test_while():
    examine('while True:\n    a = x')
    examine('while False:\n    a = x\nelse:\n    b = x')

#-------------------------------------------------------------------------------
# FunctionDef

def test_functiondef():
    examine('def foo():\n    pass')
    examine('@dec1\n@dec2(a, 1)\ndef foo():\n    pass')
    examine('def foo(a, b):\n    pass')
    examine('def foo(a, b, c=3):\n    pass')
    if VER < '3':
        examine('def foo(a, b, c=3, *args, **kwargs):\n    pass')
    else:
        examine('def foo(a, b, *args, c=3, **kwargs):\n    pass')
    examine('def foo(c=3, *args, **kwargs):\n    pass')
    examine('def foo(*args):\n    pass')
    examine('def foo(**kwargs):\n    pass')

    if VER >= '3':
        examine("def foo(a: 'ann', b=1, c=2, *d, e, f=3, **g) -> 'r':\n    pass")

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
