#-------------------------------------------------------------------------------
# seq_list_nested

def test_seq_list_nested():
    from syn.base_utils import seq_list_nested

    assert seq_list_nested(2, 0) == [1]
    assert seq_list_nested(2, 1) == [1, [2, 3]]
    assert seq_list_nested(2, 2) == [1, [2, [3,4], 5, [6,7]]]
    assert seq_list_nested(2, 2, top_level=False) == \
        ([1, [2, [3,4], 5, [6,7]]], 7)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
