from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from pytest import raises


def assert_ast_neq(c1: str, c2: str):
    u1 = FunctionDefinitionUnifier(c1)
    u2 = FunctionDefinitionUnifier(c2)
    assert u1.unified_ast_dump != u2.unified_ast_dump


def test_rename_global_variable():
    c1 = """
    def foo():
        return global_var1
    """

    c2 = """
    def foo():
        return global_var2
    """

    assert_ast_neq(c1, c2)


def test_rename_get_attribute():
    c1 = """
    def foo(a):
        return a.b
    """

    c2 = """
    def foo(a):
        return a.c
    """

    assert_ast_neq(c1, c2)


def test_rename_get_slice():
    c1 = """
    def foo(a):
        return a["b"]
    """

    c2 = """
    def foo(a):
        return a["c"]
    """

    assert_ast_neq(c1, c2)
