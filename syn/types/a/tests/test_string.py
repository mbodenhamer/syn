from six import PY2
from nose.tools import assert_raises
from syn.types.a import Type, String, Unicode, Bytes, \
    hashable, serialize, deserialize, estr, rstr
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent

#-------------------------------------------------------------------------------
# String

def test_string():
    s = u'abc'

    t = Type.dispatch(s)
    assert isinstance(t, String)

    if PY2:
        assert type(t) is Unicode
    else:
        assert type(t) is String

    assert hashable(s) == t.hashable() == s
    assert is_hashable(s)
    assert is_hashable(hashable(s))

    for cls in String.__subclasses__():
        if cls.type is None:
            continue

        val = cls.generate()
        assert type(val) is cls.type
        assert is_hashable(hashable(val))
        assert deserialize(serialize(val)) == val
    
        assert isinstance(rstr(val), str)
        assert eval(estr(val)) == val

        # for item in enumerate_(cls, max_enum=1):
        #     assert type(item) is cls.type

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
