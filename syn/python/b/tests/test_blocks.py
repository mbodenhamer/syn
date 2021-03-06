from nose.tools import assert_raises
from .test_statements import examine
from syn.util.log.b import Logger
from syn.python.b import Block, If, Num, Assign, Name, Return, Module, ProgN, \
    For, While, Call, Arg, Arguments, FunctionDef, Str
from syn.base_utils import pyversion, collection_equivalent

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
    assert_raises(TypeError, if2.validate) # Indeed, this isn't valid python
    if2r = if2.expressify_statements().resolve_progn()
    assert isinstance(if2r, ProgN) # Bad

    if2m = Module(if2)
    if2r = if2m.expressify_statements().resolve_progn()
    assert isinstance(if2r, Module) # Good
    if2r.validate()
    assert if2r.emit() == '''x = 2
if x:
    return 5'''

    if3 = Module(If(Assign([Name('x')], Num(2)),
                    [Assign([Name('y')], Name('x'))]))
    if3r = if3.expressify_statements().resolve_progn()
    if3r.validate()
    assert if3r.emit() == '''x = 2
if x:
    y = x'''
    assert if3r.variables() == {'x', 'y'}
    assert collection_equivalent(if3r._children[1]._children,
                                 [Assign([Name('y')], Name('x')), Name('x')])

    if4 = If(Num(1),
             [Num(2)],
             [Num(3)])
    assert if4.emit() == 'if 1:\n    2\nelse:\n    3'
    if4v = if4.as_value()
    assert isinstance(if4v, ProgN)
    assert if4v.value() == Name('_gensym_0')
    assert Module(if4v).resolve_progn().emit() == '''if 1:
    _gensym_0 = 2
else:
    _gensym_0 = 3'''

    if5 = If(Num(1),
             [Assign([Name('x')], Num(2))],
             [Num(3)])
    assert if5.emit() == 'if 1:\n    x = 2\nelse:\n    3'
    assert Module(if5.as_value()).resolve_progn().emit() == '''if 1:
    x = 2
else:
    x = 3'''

    if6 = If(Num(1),
             [Num(2)],
             [Assign([Name('x')], Num(3))])
    assert if6.emit() == 'if 1:\n    2\nelse:\n    x = 3'
    assert Module(if6.as_value()).resolve_progn().emit() == '''if 1:
    x = 2
else:
    x = 3'''

    if7 = If(Num(1),
             [Assign([Name('y')], Num(2))],
             [Assign([Name('x')], Num(3))])
    assert if7.emit() == 'if 1:\n    y = 2\nelse:\n    x = 3'
    assert Module(if7.as_value()).resolve_progn().emit() == '''if 1:
    y = 2
else:
    x = 3
    y = x'''

    lgr = Logger()
    if8 = If(If(Assign([Name('x')],
                       Num(2)),
                [Num(3)],
                [Num(4)]),
             [Return(Num(5))])
    assert_raises(TypeError, if8.validate)
    print(if8.viewable().pretty())
    ex = Module(if8).expressify_statements(logger=lgr)
    print(ex.viewable().pretty())
    re = ex.resolve_progn(logger=lgr)
    print(re.viewable().pretty())

    for depth, event in lgr.root[1].depth_first(yield_depth=True):
        print('-' * 80)
        print(event.display(depth))

    print(lgr.plaintext())
    assert len(lgr.nodes) > 10

    re.validate()
    assert re.emit() == '''x = 2
if x:
    _gensym_0 = 3
else:
    _gensym_0 = 4
if _gensym_0:
    return 5'''

#-------------------------------------------------------------------------------
# For

def test_for():
    examine('for x in [1, 2]:\n    a = x\n    b = y')
    examine('for x in (1, 2):\n    a = x\nelse:\n    b = x')

    f = For(Name('x'),
            Name('lst'),
            [Call(Name('x'))])
    assert f.emit() == \
'''for x in lst:
    x()'''

    f = For(Name('x'),
            Name('lst'),
            [Call(Name('x'))],
            [Call(Name('foo'), [Name('lst')])])
    assert f.emit() == \
'''for x in lst:
    x()
else:
    foo(lst)'''
    assert f.emit(indent_level=1) == \
'''    for x in lst:
        x()
    else:
        foo(lst)'''

#-------------------------------------------------------------------------------
# While

def test_while():
    examine('while True:\n    a = x')
    examine('while False:\n    a = x\nelse:\n    b = x')

    w = While(Num(1),
              [Call(Name('x'))])
    assert w.emit() == \
'''while 1:
    x()'''

    w = While(Num(1),
              [Call(Name('x'))],
              [Call(Name('y'))])
    assert w.emit() == \
'''while 1:
    x()
else:
    y()'''
    assert w.emit(indent_level=1) == \
'''    while 1:
        x()
    else:
        y()'''

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

    if VER >= '3':
        a = Arg('x')
        assert a.emit() == 'x'

        a = Arg('x', Str('foo'))
        assert a.emit() == "x: 'foo'"

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
