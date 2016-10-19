from syn.base_utils import capture

#-------------------------------------------------------------------------------
# REPL

def test_repl():
    from syn.base_utils import REPL, repl_command

    class R1(REPL):
        @repl_command('a', 'foo')
        def foo(self):
            print("foo!")

        @repl_command('b', 'RuntimeError')
        def rterr(self):
            raise RuntimeError('error!')


    def last_line(si):
        return si.getvalue().split('\n')[-2]

    r1 = R1('r1> ')
    with capture() as (out, err):
        r1._eval('a')
        assert last_line(out) == 'foo!'

        r1._eval('zzz')
        assert last_line(out) == 'Unrecognized command: zzz'

        r1._eval('b')
        assert last_line(out) == 'Error in b: RuntimeError: error!'

        r1._eval('e "1 + 2"')
        assert last_line(out) == '3'

        r1._eval('h')
        assert last_line(out) == ' h               display available commands'

    # Test launching r1() in a subprocess and passing a couple of
    # commands, checking stdout, and then passing in Ctrl-D to end;
    # verify it ended



    # Test overriding e in a REPL subclass

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
