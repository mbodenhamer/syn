from six import PY2, PY3
from syn.five import xrange
from syn.types.a import Type, String, Unicode, \
    hashable, serialize, deserialize, estr, rstr, generate, visit, find_ne, \
    DifferentLength, DiffersAtIndex, Basestring, primitive_form
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, subclasses, \
    on_error, elog, ngzwarn, is_unique

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------
# string_enumval

def test_string_enumval():
    from syn.types.a.string import string_enumval, _STRING_ENUMVALS

    assert string_enumval(0) == ''
    assert string_enumval(1) == ' '
    assert string_enumval(95) == '~'
    assert string_enumval(96) == '  '
    assert string_enumval(97) == ' !'
    assert string_enumval(190) == ' ~'
    assert string_enumval(191) == '! '
    assert string_enumval(192) == '!!'
    assert string_enumval(300) == '".'
    assert string_enumval(10000) == ' )8'

    assert 0 not in _STRING_ENUMVALS
    assert _STRING_ENUMVALS[1] == ' '
    assert _STRING_ENUMVALS[192] == '!!'

#-------------------------------------------------------------------------------

def examine_string(cls, val):
    assert type(val) is cls.type
    assert is_hashable(hashable(val))
    assert deserialize(serialize(val)) == val
    assert deserialize(serialize(cls.type)) is cls.type
    assert isinstance(rstr(val), str)
    assert primitive_form(val) == val

    assert list(visit(val)) == list(val)
    assert find_ne(val, val) is None

    eitem = eval(estr(val))
    assert eitem == val
    assert type(eitem) is cls.type

#-------------------------------------------------------------------------------
# String

def test_string():
    s = u'abc'

    t = Type.dispatch(s)
    assert isinstance(t, String)

    if PY2:
        assert type(t) is Unicode
        examine_string(Unicode, s)
    else:
        assert type(t) is String
        examine_string(String, s)

    assert hashable(s) == t.hashable() == s
    assert is_hashable(s)
    assert is_hashable(hashable(s))

    assert find_ne('abc', 'abcd') == DifferentLength('abc', 'abcd')
    assert find_ne('abcd', 'abc') == DifferentLength('abcd', 'abc')
    assert find_ne('abc', 'abd') == DiffersAtIndex('abc', 'abd', 2)

    for cls in subclasses(String, [String]):
        if cls.type is None or cls is Basestring:
            continue

        for k in xrange(SAMPLES):
            val = generate(cls.type)
            with on_error(elog, examine_string, (cls, val)):
                examine_string(cls, val)

        x = 0
        buf = []
        last = None
        for item in enumerate_(cls.type, max_enum=SAMPLES * 10, step=100):
            assert type(item) is cls.type
            assert item != last
            buf.append(item)
            last = item
            x += 100

        assert is_unique(buf)

    # estr potential edge cases

    cases = ["abc'de\r7fghi", "\x00", "\\", "\'", '\"', '\a', '\b', '\t', '\v',
             u'\u2013', '\\u2']
    for case in cases:
        assert eval(estr(case)) == case

#-------------------------------------------------------------------------------
# Unicode

def test_unicode():
    if PY2:
        gen = generate(unicode)
        assert isinstance(gen, unicode)

    assert Unicode._enumeration_value(140) == u'\xab'

#-------------------------------------------------------------------------------
# Bytes

def test_bytes():
    if PY3:
        gen = generate(bytes)
        assert isinstance(gen, bytes)

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
