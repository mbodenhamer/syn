from nose.tools import assert_raises

#-------------------------------------------------------------------------------
# Topological Sort

def test_topological_sorting():
    from syn.base_utils import topological_sorting, First, Last, LE

    assert topological_sorting([LE(1, 2)]) == [1, 2]
    assert topological_sorting([LE(First, 1)]) == [1]
    assert topological_sorting([LE(1, Last)]) == [1]

    rels = [LE(First, 1),
            LE(1, 2),
            LE(2, 3),
            LE(3, Last)]
    assert topological_sorting(rels) == [1, 2, 3]

    cycle = [LE(1, 2),
             LE(2, 3),
             LE(3, 2)]
    assert_raises(ValueError, topological_sorting, cycle)

    assert_raises(ValueError, topological_sorting, [LE(1, First)])
    assert_raises(ValueError, topological_sorting, [LE(Last, 1)])

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
