import os

DIR = os.path.dirname(os.path.abspath(__file__))
FOO = os.path.join(DIR, 'foo')

#-------------------------------------------------------------------------------
# Temporary assignment

def test_assign():
    from syn.base_utils import assign

    class Foo(object):
        lst = [1, 2, 3]

    assert Foo.lst == [1, 2, 3]
    with assign(Foo, 'lst', [3, 4, 5]):
        assert Foo.lst == [3, 4, 5]
    assert Foo.lst == [1, 2, 3]

#-------------------------------------------------------------------------------
# cd

def test_chdir():
    from syn.base_utils import chdir

    pwd = os.getcwd()
    assert pwd != FOO
    with chdir(FOO):
        assert os.getcwd() == FOO != pwd
        with open('foo', 'rt') as f:
            assert f.read() == 'foo'
    assert pwd == os.getcwd() != FOO

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
