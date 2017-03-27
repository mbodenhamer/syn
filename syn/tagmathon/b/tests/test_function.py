from syn.tagmathon.b import Function, vars, Add, Sub, Mul, Set, eval

#-------------------------------------------------------------------------------
# Function

def test_function():
    a, b, c = vars('a', 'b', 'c')
    f = Function('foo', [a, b],
                 [Set(c, Add(a, b)),
                  Sub(c, Mul(b, 2))])
    
    assert eval(f(4, 3)) == 1

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
