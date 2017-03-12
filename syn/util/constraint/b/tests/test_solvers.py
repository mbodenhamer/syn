import operator as op
from functools import partial
from nose.tools import assert_raises
from syn.base_utils import collection_equivalent, first, compose
from syn.util.constraint import Problem, Domain, Constraint, Solver, \
    RecursiveBacktrackSolver, SimpleSolver, FunctionConstraint, \
    AllDifferentConstraint, EqualConstraint

#-------------------------------------------------------------------------------
# Trivial Solver Problems

def problem1(S):
    lt = FunctionConstraint(op.lt, ('a', 'b'))
    p = Problem(Domain(a=[1, 2, 3],
                       b=[2, 3]),
                [lt])

    if S is RecursiveBacktrackSolver:
        S = partial(S, selection_method='random')

    s = S(p)

    assert collection_equivalent(list(s.solutions()),
                                 [dict(a=1, b=2), 
                                  dict(a=1, b=3), 
                                  dict(a=2, b=3)])

def problem2(S):
    lt = FunctionConstraint(op.lt, ('a', 'b'))
    p = Problem(Domain(a=[3, 4],
                       b=[1, 2]),
                [lt])

    if S is RecursiveBacktrackSolver:
        S = partial(S, forward_checking=False)

    s = S(p)

    assert list(s.solutions()) == []

def problem3(S):
    lt = FunctionConstraint(op.lt, ('a', 'b'))
    p = Problem(Domain(a=int,
                       b=int),
                [lt])
    s = S(p)

    sols = list(s.solutions())
    assert sols

#-------------------------------------------------------------------------------
# Sudoku

def sudoku(S):
    strs = compose(list, partial(map, str))

    vars = {}
    values = list(range(1, 10))
    for i in range(1, 10):
        for k in range(i*10 + 1, i*10 + 10):
            vars[str(k)] = list(values)
    
    cons = []
    for i in range(1, 10):
        cons.append(AllDifferentConstraint(strs(range(i*10+1, i*10+10)))) # rows
        cons.append(AllDifferentConstraint(strs(range(10+i, 100+i, 10)))) # cols

    # 3x3 squares
    cons.append(AllDifferentConstraint(strs([11,12,13,21,22,23,31,32,33])))
    cons.append(AllDifferentConstraint(strs([41,42,43,51,52,53,61,62,63])))
    cons.append(AllDifferentConstraint(strs([71,72,73,81,82,83,91,92,93])))
    cons.append(AllDifferentConstraint(strs([14,15,16,24,25,26,34,35,36])))
    cons.append(AllDifferentConstraint(strs([44,45,46,54,55,56,64,65,66])))
    cons.append(AllDifferentConstraint(strs([74,75,76,84,85,86,94,95,96])))
    cons.append(AllDifferentConstraint(strs([17,18,19,27,28,29,37,38,39])))
    cons.append(AllDifferentConstraint(strs([47,48,49,57,58,59,67,68,69])))
    cons.append(AllDifferentConstraint(strs([77,78,79,87,88,89,97,98,99])))

    # init = [[0, 9, 0, 7, 0, 0, 8, 6, 0],
    #         [0, 3, 1, 0, 0, 5, 0, 2, 0],
    #         [8, 0, 6, 0, 0, 0, 0, 0, 0],
    #         [0, 0, 7, 0, 5, 0, 0, 0, 6],
    #         [0, 0, 0, 3, 0, 7, 0, 0, 0],
    #         [5, 0, 0, 0, 1, 0, 7, 0, 0],
    #         [0, 0, 0, 0, 0, 0, 1, 0, 9],
    #         [0, 2, 0, 6, 0, 0, 0, 5, 0],
    #         [0, 5, 4, 0, 0, 8, 0, 7, 0]]

    init = [[2, 9, 5, 7, 4, 3, 8, 6, 1],
            [4, 3, 1, 8, 6, 5, 9, 2, 7],
            [8, 7, 6, 1, 9, 2, 5, 4, 3],
            [3, 8, 7, 4, 5, 9, 2, 1, 6],
            [6, 1, 2, 3, 8, 7, 4, 9, 5],
            [5, 4, 9, 2, 1, 6, 7, 3, 8],
            [7, 6, 3, 5, 3, 4, 1, 8, 9],
            [9, 2, 8, 6, 7, 1, 3, 5, 4],
            [1, 5, 4, 9, 3, 8, 6, 7, 2]]

    for i in range(1, 10):
        for j in range(1, 10):
            if init[i-1][j-1] != 0:
                cons.append(EqualConstraint(str(i*10+j), init[i-1][j-1]))
    
    p = Problem(Domain(**vars), cons)
    s = S(p)

    #assert first(s.solutions())

#-------------------------------------------------------------------------------
# Solver

def test_solver():
    p = Problem(Domain(a=[1, 2]), [Constraint()])
    s = Solver(p)
    assert_raises(NotImplementedError, s.solutions)

#-------------------------------------------------------------------------------
# Simple

def test_simple_solver():
    problem1(SimpleSolver)
    problem2(SimpleSolver)
    problem3(SimpleSolver)

#-------------------------------------------------------------------------------
# Recursive Backtrack

def test_recursive_backtrack_solver():
    sudoku(RecursiveBacktrackSolver)
    problem1(RecursiveBacktrackSolver)
    problem2(RecursiveBacktrackSolver)
    problem3(RecursiveBacktrackSolver)


#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
