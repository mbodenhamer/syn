from syn.util.log.b import StringEvent, Logger, Event

#-------------------------------------------------------------------------------
# String Event

def test_stringevent():
    s = StringEvent(s='abc')
    assert s.plaintext() == 'StringEvent(abc)'

    l = Logger()
    l.add(s)
    l.push(StringEvent(s='def'))
    l.add(StringEvent(s='ghi'))

    assert l.current_parent.s == 'def'
    l.pop()
    assert l.current_parent is l.root
    l.reset()
    assert l.current_parent is l.root

    assert l.plaintext() == '''StringEvent(abc)
StringEvent(def
 StringEvent(ghi))'''

    assert StringEvent().plaintext() == 'StringEvent()'

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
