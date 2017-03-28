from syn.tagmathon.b import Function, vars, Add, Sub, Mul, Set, eval, \
    compile_to_python

#-------------------------------------------------------------------------------
# Function

def test_function():
    a, b, c = vars('a', 'b', 'c')
    f = Function('foo', [a, b],
                 [Set(c, Add(a, b)),
                  Sub(c, Mul(b, 2))])
    
    assert eval(f(4, 3)) == 1
    assert compile_to_python(f(4, 3)) == 'foo(4, 3)'
    assert compile_to_python(f) == '''def foo(a, b):
    c = (a + b)
    return (c - (b * 2))'''

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
