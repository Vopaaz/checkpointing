from checkpointing.refactor.unify.funcdef import FunctionDefinitionUnifier
from textwrap import dedent as d


def test_change_argument_name():
    u = FunctionDefinitionUnifier()

    c1 = d("""
    def foo(a):
        return a
    """)

    c2 = d("""
    def foo(b):
        return b
    """)

    assert u.unify(c1) == u.unify(c2)

