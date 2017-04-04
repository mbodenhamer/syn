from syn.tagmathon.b import Function, vars, Add, Sub, Mul, If, LE, Set, eval, \
    compile_to_python, Variable, Eq, Assert

#-------------------------------------------------------------------------------
# Function

def test_function():
    a, b, c = vars('a', 'b', 'c')
    f = Function('foo', [a, b],
                 [Set(c, Add(a, b)),
                  Sub(c, Mul(b, 2))])
    
    assert eval(f(4, 3)) == 1
    assert eval((f, 4, 3)) == 1
    assert compile_to_python(f(4, 3)) == 'foo(4, 3)'
    assert compile_to_python((f, 4, 3)) == 'foo(4, 3)'
    assert compile_to_python(f) == '''def foo(a, b):
    c = (a + b)
    return (c - (b * 2))'''

    assert eval((If, (LE, 1, 2),
                     (Add, 5, 2),
                     (Sub, 5, 2))) == 7
    assert eval((If, (LE, 2, 1),
                     (Add, 5, 2),
                     (Sub, 5, 2))) == 3
    assert eval([(Set, c, f),
                 (c, 4, 3)]) == 1

    # TODO: distinguish between function reference and function definition
    # assert compile_to_python([(Set, c, f),
    #                           (c, 4, 3)]) == 'c = f\nc(4, 3)'
    assert compile_to_python([(Set, a, b),
                              (a, 4, 3)]) == 'a = b\na(4, 3)'


    e = Function('empty', [], [])
    assert eval(e()) is None
    assert compile_to_python(e) == '''def empty():\n    pass'''

    fact = Function('fact', [a], [])
    fact.body = [If(LE(a, 0),
                    1,
                    Mul(a, fact(Sub(a, 1))))]

    assert eval(fact(0)) == 1
    assert eval(fact(2)) == 2
    assert eval(fact(3)) == 6
    assert eval(fact(5)) == 120
    assert eval(fact(6)) == 720
    assert compile_to_python(fact) == '''def fact(a):
    if (a <= 0):
        1
    else:
        (a * fact((a - 1)))'''

    x, y = vars('x', 'y')
    foo = Function('foo', [x],
                   [Add(x, y)])
    bar = Function('bar', [y],
                   [foo(1991)])
    assert eval([Set(y, 0), foo(3)]) == 3
    assert eval([Set(y, 0), bar(100)]) == 2091


    fact = Variable('fact')
    eval([Function(fact, [a], 
                   (If, (LE, a, 0),
                         1,
                        (Mul, a, (fact, (Sub, a, 1))))),
          (Assert, (Eq, (fact, 5), 120)),
         ])


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
