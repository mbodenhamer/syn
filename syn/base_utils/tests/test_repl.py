from syn.base_utils import capture, assign

#-------------------------------------------------------------------------------
# REPL

def test_repl():
    from syn.base_utils import repl_command
    import syn.base_utils.repl as repl

    class R1(repl.REPL):
        commands = dict(repl.REPL.commands)
        command_help = dict(repl.REPL.command_help)

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
        assert last_line(out) == 'Error in b: ***RuntimeError***: error!'

        r1._eval('e "1 + 2"')
        assert last_line(out) == '3'

        r1._eval('h')
        assert last_line(out) == ' q               quit'

        fi_count = []
        def fake_input(prompt):
            fi_count.append(1)

            N = sum(fi_count)
            if N <= 4:
                return 'e {}'.format(N)
            else:
                raise EOFError

        def fake_input2(prompt):
            fi_count.append(1)
            return 'q'

        assert sum(fi_count) == 0
        with assign(repl, 'raw_input', fake_input):
            r1()
            assert last_line(out) == '4'
            
        assert sum(fi_count) == 5
        with assign(repl, 'raw_input', fake_input2):
            r1()
        assert sum(fi_count) == 6

    # Test overriding e in a REPL subclass
    class R2(R1):
        @repl_command('e', 'bar')
        def bar(self, *args):
            print("bar!")

    r2 = R2('r2> ')
    with capture() as (out, err):
        r2._eval('a')
        assert last_line(out) == 'foo!'

        r2._eval('e "1 + 2"')
        assert last_line(out) == 'bar!'

    assert len(repl.REPL.commands) == 4
    assert len(repl.REPL.command_help) == 4

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
