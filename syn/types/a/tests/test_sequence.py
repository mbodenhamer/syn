from six import PY2
from syn.five import xrange
from nose.tools import assert_raises
from syn.types.a import Type, Sequence, List, Tuple, \
    hashable, serialize, deserialize, estr, rstr, visit, find_ne, \
    DifferentLength, DiffersAtIndex, deep_feq, feq_comp, ValueExplorer
from syn.types.a import enumerate as enumerate_
from syn.base_utils import is_hashable, assert_equivalent, elog, ngzwarn, \
    is_unique, on_error

from syn.globals import TEST_SAMPLES as SAMPLES
SAMPLES //= 10
SAMPLES = max(SAMPLES, 1)
ngzwarn(SAMPLES, 'SAMPLES')

#-------------------------------------------------------------------------------

def examine_sequence(cls, val):
    assert type(val) is cls.type
    assert is_hashable(hashable(val))
    sval = deserialize(serialize(val))
    #import ipdb; ipdb.set_trace()
    assert deep_feq(sval, val)
    assert isinstance(rstr(val), str)

    assert list(visit(val)) == list(val)
    assert find_ne(val, val) is None

    eitem = eval(estr(val))
    #assert deep_feq(eitem, val)
    assert type(eitem) is cls.type

#-------------------------------------------------------------------------------
# Sequence

def test_sequence():
    l = [1, 2.3, 'abc']
    t = Type.dispatch(l)
    assert isinstance(t, Sequence)
    assert type(t) is List
    if PY2:
        assert set(hashable(l)) == set(t.hashable()) == \
            {'__builtin__.list', 1, 2.3, 'abc'}
    else:
        assert set(hashable(l)) == set(t.hashable()) == \
            {'builtins.list', 1, 2.3, 'abc'}

    assert not is_hashable(l)
    assert is_hashable(hashable(l))

    l1 = [1, 2, 3]
    l2 = [1, 2, 3, 4]
    l3 = [1, 2, 4]
    assert find_ne(l1, l2) == DifferentLength(l1, l2)
    assert find_ne(l2, l1) == DifferentLength(l2, l1)
    assert find_ne(l1, l3) == DiffersAtIndex(l1, l3, 2)

    tup = tuple(l)
    examine_sequence(List, l)
    examine_sequence(Tuple, tup)

    # s = (-4408727817343147023, set([(1.0882961461171937e+308-9.002895540558738e+307j), True, 50776551713211937797672894513551405838221237202405843969L, False, (1.7408773247076246e+308+1.3203219649799925e+308j), (-1.1131902479010353e+307+1.3425410256468193e+308j), (5.21462034181984e+307-1.7443593939936275e+308j), u'\U00048ed7\u3fbc\U000f18d3\U000e102c\U0009dfd7\U000ee498\U0005aa4b\U000f67c6\U0010d82c\U00056444\U000ee4c4\U000cffd6\U0010d123\U000d358b\U00087589\U000819f7\U000648bc\U000c61d2\U00049934\U00080021\U000be8cf\U000e136c\u1872\U00108fee\U000935e4\U000c2a9a\U00033814\U00071611\U0002c59b\U0009234b\u85af\U000f6c3e\U0002ca91\U000f5aac\U0010b46d\U000c762f\U0002dc59\U000a7958\U00096beb\U0003812e\U00069fda\U0005fdf9\U0005a344\U000ca766\U000369bf\U00105737\U000ddcad\U00073f89\U000aa779\U0006b413\U000f0bcd\U00107da3\U00093376\U0003b198\U00017c62\U000cef9a\U000f0976\U000d35a7\U000b4d50\U000da8b0\U00062e84\U000d0f03\uf990\ucf87\U0005b61b\U000ae9d7\U000646b0\U00065b37\U00052485\U000cf97a\U000b81d5\U000b9dd6\U000941ce\U000f1154\U000c1d21\U000ac889\U000af498\U0009b59b\U0006c583\U000d70ce\U0007176e\U000e5550\U000a0f5a\U0002721a\U000364f9\uf639', 988182643622121392997607692957847081838395265554283050928L, "\x925\x1a\x8b\xc8ZXM\x82ni\x8e\x17\x0e\x9eo\x8e\xf7\xcf\xfe'\xfew]\xa6\xee\x83c-\xdf\xcal\x0c\x06\xe4\xad\xeer:\xa1.[2\x89\x12Q\x16\xb4\x83\x06\xfcs \x1f\x92\x86W\xc9>\xce\xfawLPcF\xfft\xf4\xf6H\xc1\xed'\xd3F\x17\xf6\x94_", 1.487538128898748e+307, -2123852387664102928147391086961520200152928947390467236743279L, '\xae\xe2H\x9dP\xdc\x94\xbe\xa1\\ww\xc3,\xcfJ\xcbL\x15\x8a\xea\xa0\x04\xa0\x0ft!\xf1\xe6/\xf0\xc1q1\t', '\xe8\x81&\x82VO\x8dY\n\n\x1f\x18\xe4\xfe\xcf]\x88aQ\xad\xa7\xfek\xc5\xe8\x13=\x89\xc0\x04\xe4\xf2#r\xea\xa9]\xeeU\xab\x0b\xf3\xfd\xd7K\xce', None, '']), False)
    # print list(visit(s[1]))
    # x = ValueExplorer(s)
    # import ipdb; ipdb.set_trace()
    # for val in x.depth_first():
    #     print(val)

    for cls in Sequence.__subclasses__():
        for k in xrange(SAMPLES):
            val = cls.generate()
            with on_error(elog, examine_sequence, (cls, val)):
                examine_sequence(cls, val)

        buf = []
        last = None
        for item in enumerate_(cls.type, max_enum=SAMPLES * 10, step=100):
            assert type(item) is cls.type
            assert item != last
            buf.append(item)
            last = item

        assert is_unique(buf)

    assert list(visit(l, enumerate=True)) == [(0, 1), (1, 2.3), (2, 'abc')]
    assert list(visit([])) == []

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
