from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from pytest import raises

u = FunctionDefinitionUnifier()


def assert_ast_neq(c1: str, c2: str):
    assert u.get_unified_ast_dump(c1) != u.get_unified_ast_dump(c2)


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