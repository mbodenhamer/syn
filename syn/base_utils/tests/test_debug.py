import sys
from nose.tools import assert_raises

#-------------------------------------------------------------------------------
# Trace

def test_trace():
    from syn.base_utils import Trace

    t = Trace()
    assert t(None, 'c_call', None) is t
    assert t(None, 'c_exception', None) is t
    assert t(None, 'c_return', None) is t
    assert t(None, 'call', None) is t
    assert t(None, 'exception', None) is t
    assert t(None, 'line', None) is t
    assert t(None, 'return', None) is t
    assert_raises(RuntimeError, t, None, 'foo', None)

#-------------------------------------------------------------------------------
# call_trace

def test_call_trace():
    from syn.base_utils import call_trace, reset_trace, capture, CallTrace

    def foo():
        bar()

    def bar():
        pass

    foo()
    tr = sys.gettrace()
    with capture() as (out, err):
        with reset_trace():
            call_trace()
            foo()
    assert sys.gettrace() is tr

    assert out.getvalue() == 'foo\n bar\n__exit__\n reset_trace\n'
    assert err.getvalue() == ''

    t = CallTrace()
    with capture() as (out, err):
        t(sys._getframe(), 'call', None)
    
    assert out.getvalue() == 'test_call_trace\n'
    assert err.getvalue() == ''
    assert t.indent == 1

    t(sys._getframe(), 'return', None)
    assert t.indent == 0

    # def foo2():
    #     foo2()

    # import pdb
    # from syn.base_utils import getfunc
    # class MyTrace(CallTrace):
    #     def __init__(self, pred=None, indent=0, tab=' '):
    #         super(MyTrace, self).__init__(indent, tab)
    #         self.stack = []
    #         self.pred = pred if pred is not None else lambda s: False

    #     def call(self, frame, arg):
    #         super(MyTrace, self).call(frame, arg)
    #         self.stack.append(frame.f_code.co_name)
    #         if getfunc(self.pred)(self.stack):
    #             ret = pdb.Pdb()
    #             ret.reset()
    #             return ret.dispatch_call(frame, arg)
    #         return self

    #     def return_(self, frame, arg):
    #         super(MyTrace, self).return_(frame, arg)
    #         self.stack.pop()
    #         return self

    # filt = lambda s: len(list(filter(lambda x: x == 'foo2', s))) >= 3
    # with reset_trace():
    #     sys.settrace(MyTrace(filt))
    #     foo2()

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
