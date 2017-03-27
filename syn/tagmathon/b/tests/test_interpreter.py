from nose.tools import assert_raises
from syn.tagmathon.b import Frame, Variable, Env, eval

#-------------------------------------------------------------------------------
# Frame

def test_frame():
    f = Frame()
    f['a'] = 1
    f['b'] = 2

    assert f.globals == {}
    assert f.locals == dict(a=1, b=2)

    f.set_global('a', 3)
    f.set_global('c', 4)

    assert f['a'] == 1
    assert f['b'] == 2
    assert f['c'] == 4

    assert len(f) == 3
    assert list(f) == ['a', 'b', 'c']

    del f['a']
    assert f['a'] == 3
    del f['a']
    assert_raises(KeyError, f.__getitem__, 'a')
    assert_raises(KeyError, f.__delitem__, 'a')

    f.update(dict(a=1))
    assert f.locals == dict(a=1, b=2)

#-------------------------------------------------------------------------------
# Env

def test_env():
    e = Env()
    e['a'] = 1
    e['b'] = 2
    assert dict(e.items()) == dict(a=1, b=2)
    
    e.push({})
    e['a'] = 3
    e['c'] = 4
    assert dict(e.items()) == dict(a=3, b=2, c=4)

    e.pop()
    assert dict(e.items()) == dict(a=1, b=2)

    e.update(dict(a=3, c=4))
    assert dict(e.items()) == dict(a=3, b=2, c=4)

    del e['c']
    assert dict(e.items()) == dict(a=3, b=2)

    assert len(e) == 2
    assert list(e) == ['a', 'b']

    e.set_global('a', 4)
    assert e['a'] == 3
    del e['a']
    assert e['a'] == 4

#-------------------------------------------------------------------------------
# eval

def test_eval():
    assert eval(1) == 1

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
