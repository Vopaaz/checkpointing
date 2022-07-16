from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from pytest import raises


def assert_ast_neq(c1: str, c2: str):
    u1 = FunctionDefinitionUnifier(c1)
    u2 = FunctionDefinitionUnifier(c2)
    assert u1.unified_ast_dump != u2.unified_ast_dump


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


def test_change_get_slice():
    c1 = """
    def foo(a):
        return a["b"]
    """

    c2 = """
    def foo(a):
        return a["c"]
    """

    assert_ast_neq(c1, c2)

def test_different_internal_lambda_logic():
    c1 = """
    def foo(a):
        f = lambda x: x + 1
        return f(a)
    """

    c2 = """
    def foo(a):
        f = lambda x: x - 1
        return f(a)
    """

    assert_ast_neq(c1, c2)

def test_async_function_def_is_considered_different():
    c1 = """
    def foo():
        pass
    """

    c2 = """
    async def foo():
        pass
    """

    assert_ast_neq(c1, c2)

def test_assign_starred_but_different_number_of_elements():
    c1 = """
    def foo():
        [a1, a2, *a3] = baz
    """

    c2 = """
    def bar():
        [x1, *x2] = baz
    """

    assert_ast_neq(c1, c2)
