import operator as op
from functools import partial
from syn.types import hashable
from nose.tools import assert_raises
from syn.util.constraint import Problem, Domain, Constraint, Solver, \
    RecursiveBacktrackSolver, SimpleSolver, FunctionConstraint

#-------------------------------------------------------------------------------
# Solver Problems

def problem1(S):
    lt = FunctionConstraint(op.lt, ('a', 'b'))
    p = Problem(Domain(a=[1, 2, 3],
                       b=[2, 3]),
                [lt])
    s = S(p)

    assert set(hashable(list(s.solutions()))) == \
        set(hashable([dict(a=1, b=2), dict(a=1, b=3),
                      dict(a=2, b=3)]))

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
    problem1(RecursiveBacktrackSolver)
    problem2(RecursiveBacktrackSolver)
    problem3(RecursiveBacktrackSolver)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
