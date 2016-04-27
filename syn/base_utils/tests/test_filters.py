from syn.base_utils import split, join, dictify_strings

#-------------------------------------------------------------------------------
# String

def test_split():
    assert split('a  b\tc') == ['a', 'b', 'c']
    assert split('a,b,c') == ['a,b,c']
    assert split('a,b,c', sep=',') == ['a', 'b', 'c']

#-------------------------------------------------------------------------------
# Sequence

def test_join():
    assert join(('a', 'b')) == 'a b'
    assert join(['a', 'b'], sep=',') == 'a,b'

def test_dictify_strings():
    assert dictify_strings(['a', 'b']) == dict(a = '', b = '')
    assert dictify_strings(['a b', 'c d'], empty=False) == dict(a='b', c='d')
    assert dictify_strings(['a,b', 'c,d'], sep=',') == dict(a='b', c='d')
    assert dictify_strings(['a,b', 'c,d'], sep=',', empty=True) == \
        {'a,b': '', 'c,d': ''}

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
