from nose.tools import assert_raises

#-------------------------------------------------------------------------------
# Topological Sort

def test_topological_sorting():
    from syn.base_utils import topological_sorting, Precedes, Succeeds

    assert topological_sorting([], [Precedes(1, 2)]) == [1, 2]

    rels = [Precedes(1, 2),
            Precedes(2, 3)]
    assert topological_sorting([], rels) == [1, 2, 3]

    rels = [Precedes(1, 10),
            Succeeds(10, 2)]
    sort = topological_sorting([], rels)
    assert sorted(sort) == [1, 2, 10]
    assert sort[0] == 1 or sort[0] == 2
    assert sort[-1] == 10

    cycle = [Precedes(1, 2),
             Precedes(2, 3),
             Precedes(3, 2)]
    assert_raises(ValueError, topological_sorting, [], cycle)

    sort = topological_sorting([1, 2, 3], [Precedes(2, 3)])
    assert sorted(sort) == [1, 2, 3]
    assert sort.index(2) < sort.index(3)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
