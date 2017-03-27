from syn.tagmathon.b import Function, vars, Add, Sub, eval

#-------------------------------------------------------------------------------
# Function

def test_function():
    a, b = vars('a', 'b')
    f = Function('foo', [a, b],
                 [Add(a, b),
                  Sub(a, b)])
    
    assert eval(f(4, 3)) == 1

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
