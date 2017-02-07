from nose.tools import assert_raises
from syn.five import PY2
from syn.base import Base, Attr
from syn.base_utils import assert_type_equivalent, pretty

#-------------------------------------------------------------------------------
# String-Quoting Utils

def test_quote_string():
    from syn.base_utils import quote_string

    assert quote_string('abc') == "'abc'"
    assert quote_string(u'\u2013') == u"'\u2013'"
    assert quote_string("ab'c") == '"ab\'c"'
    assert quote_string('ab"c"') == "'ab\"c\"'"
    assert quote_string('''a'b"c"''') == """'''a'b"c"'''"""

    evil = "\"\"\"'''a'b\"c\"'''\"\"\""
    assert quote_string("""'''a'b"c"'''""") == evil
    assert quote_string(evil) == '\'"""\'\'\'a\'b"c"\'\'\'"""\''

    uevil = u"\"\"\"'''\u2013'b\"c\"'''\"\"\""
    assert quote_string(uevil) == u'\'"""\'\'\'\u2013\'b"c"\'\'\'"""\''

def test_outer_quotes():
    from syn.base_utils import outer_quotes

    assert outer_quotes('"abc"') == '"'
    assert outer_quotes("'abc'") == "'"
    assert outer_quotes('\'abc\'') == "'"
    assert outer_quotes("'''abc'''") == "'''"
    assert outer_quotes('"""abc"""') == '"""'
    assert outer_quotes("''") == "'"
    assert outer_quotes("''''''") == "'''"
    assert outer_quotes('""') == '"'
    assert outer_quotes('""""""') == '"""'

    # Gotchas
    assert outer_quotes('""a"') == '"'

    assert_raises(ValueError, outer_quotes, 'abc')
    assert_raises(ValueError, outer_quotes, '"abc')
    assert_raises(ValueError, outer_quotes, 'abc"')
    assert_raises(ValueError, outer_quotes, '"abc\'')

def test_break_quoted_string():
    from syn.base_utils import break_quoted_string
    
    assert break_quoted_string('"abc"', '1') == '"abc"'
    assert break_quoted_string('"ab1c"', '1') == '"ab"1"c"'
    assert break_quoted_string('"ab1c1d2e"', '1', '2') == '"ab"2"c"2"d2e"'
    assert break_quoted_string('"ab"2"c"2"d2e"', '2') == '"ab"2"c"2"d"2"e"'

def test_break_around_line_breaks():
    from syn.base_utils import break_around_line_breaks

    assert break_around_line_breaks('"abc"') == '"abc"'
    assert break_around_line_breaks('"ab\nc"') == '"ab"\n"c"'
    assert break_around_line_breaks('"ab\rc"') == '"ab"\n"c"'
    assert break_around_line_breaks('"ab\r\nc"') == '"ab"\n"c"'
    assert break_around_line_breaks('"a\nb\r\nc\rd"') == '"a"\n"b"\n"c"\n"d"'

def test_escape_line_breaks():
    from syn.base_utils import escape_line_breaks

    assert escape_line_breaks('abc') == 'abc'
    assert escape_line_breaks('a\r\nb\rc\n') == 'a\\r\\nb\\rc\\n'

def test_escape_null():
    from syn.base_utils import escape_null

    assert escape_null('abc') == 'abc'
    assert escape_null('a\x00b\x00c') == 'a\\x00b\\x00c'

def test_escape_for_eval():
    from syn.base_utils import escape_for_eval

    assert escape_for_eval('abc') == 'abc'
    assert escape_for_eval('\n') == '\\n'
    assert escape_for_eval('b\\a') == 'b\\\\a'

#-------------------------------------------------------------------------------
# String Creation

def test_chrs():
    from syn.base_utils import chrs
    
    assert chrs([97,98,10]) == 'ab\n'

#-------------------------------------------------------------------------------
# Unicode issues

def test_safe_chr():
    from syn.base_utils import safe_chr

    assert safe_chr(32) == ' '
    assert safe_chr(256) == u'\u0100'

def test_safe_str():
    from syn.base_utils import safe_str

    s = u'ab\u2013cd'
    if PY2:
        assert safe_str(s) == s.encode('utf-8')
    else:
        assert safe_str(s) == s

def test_safe_unicode():
    from syn.base_utils import safe_unicode

    s = '\xac\xab'
    assert safe_unicode(s) == u'\xac\xab'

def test_safe_print():
    from syn.base_utils import safe_unicode, safe_print
    from syn.base_utils import capture, chrs

    with capture() as (out, err):
        s = safe_unicode('\xac\xab')
        safe_print(s)

    if PY2:
        assert out.getvalue() == '\xc2\xac\xc2\xab\n'
    else:
        assert out.getvalue() == chrs([172, 171, 10])

#-------------------------------------------------------------------------------
# istr

class IstrTest(Base):
    _attrs = dict(a = Attr(int))

class List1(list):
    pass

class Tuple1(tuple):
    pass

class Set1(set):
    pass

class Dict1(dict):
    pass

def test_istr():
    from syn.base_utils import istr

    cases = {'1': 1,
             '1.2': 1.2,
             "'abc'": 'abc',
             "[1, 1.2, 'abc']": [1, 1.2, 'abc'],
             "IstrTest(a = 1)": IstrTest(a = 1),
             "IstrTest": IstrTest,
             "(1, 1.2, 'abc')": (1, 1.2, 'abc'),
             "set([1])": set([1]),
             "List1([1, 1.2])": List1([1, 1.2]),
             "Tuple1([1, 1.2])": Tuple1([1, 1.2]),
             "Set1([1, 1.2])": Set1([1, 1.2]),
             "{'a': 1}": dict(a = 1),
             "Dict1({'a': 1})": Dict1(a = 1),
             }

    py2_cases = {"u'abc'": u'abc'}
    py3_cases = {"'abc'": u'abc'}

    for strval, val in cases.items():
        ival = istr(val)
        assert ival == strval
        assert_type_equivalent(eval(ival), val)

    if PY2:
        for strval, val in py2_cases.items():
            ival = istr(val)
            assert ival == strval
            assert_type_equivalent(eval(ival), val)
    else:
        for strval, val in py3_cases.items():
            ival = istr(val)
            assert ival == strval
            assert_type_equivalent(eval(ival), val)

    ival = istr({1, 1.2})
    assert ival == "{1, 1.2}" or ival == "{1.2, 1}"

    lst = [1, 1.2, 'abc']
    lst_istr = "[1,\n 1.2,\n 'abc']"
    assert istr(lst, pretty=True) == lst_istr

    dct = {'a': [1, 1.2]}
    dct_istr = \
'''{'a': [1,
       1.2]}'''

    assert pretty(dct) == dct_istr

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
