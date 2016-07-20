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
