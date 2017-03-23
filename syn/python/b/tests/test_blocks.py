from .test_statements import examine
from syn.python.b import Block

#-------------------------------------------------------------------------------
# Block

def test_block():
    Block

#-------------------------------------------------------------------------------
# If

def test_if():
    examine('if 1:\n    a = 1')
    examine('if 1:\n    a = 1\nelse:\n    a = 2')
    examine('if 1:\n  a = 1\nelif 2:\n  a = 2\nelse:\n  a = 3',
            'if 1:\n    a = 1\nelse:\n    if 2:\n        a = 2\n    else:\n        a = 3')

#-------------------------------------------------------------------------------
# For

def test_for():
    examine('for x in [1, 2]:\n    a = x\n    b = y')
    examine('for x in (1, 2):\n    a = x\nelse:\n    b = x')

#-------------------------------------------------------------------------------
# While

def test_while():
    examine('while 1:\n    a = x')
    examine('while 1:\n    a = x\nelse:\n    b = x')

#-------------------------------------------------------------------------------

if __name__ == '__main__': # pragma: no cover
    from syn.base_utils import run_all_tests
    run_all_tests(globals(), verbose=True, print_errors=False)
