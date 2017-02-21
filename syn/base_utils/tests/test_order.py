from nose.tools import assert_raises

#-------------------------------------------------------------------------------
# Topological Sort

def test_topological_sorting():
    from syn.base_utils import topological_sorting, LE

    assert topological_sorting([LE(1, 2)]) == [1, 2]

    rels = [LE(1, 2),
            LE(2, 3)]
    assert topological_sorting(rels) == [1, 2, 3]

    rels = [LE(1, 10),
            LE(2, 10)]
    sort = topological_sorting(rels)
    assert sorted(sort) == [1, 2, 10]
    assert sort[0] == 1 or sort[0] == 2
    assert sort[-1] == 10

    cycle = [LE(1, 2),
             LE(2, 3),
             LE(3, 2)]
    assert_raises(ValueError, topological_sorting, cycle)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
