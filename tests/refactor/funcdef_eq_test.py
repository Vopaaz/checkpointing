from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from typing import Tuple, List


def assert_ast_eq(c1: str, c2: str):
    u1 = FunctionDefinitionUnifier(c1)
    u2 = FunctionDefinitionUnifier(c2)
    assert u1.unified_ast_dump == u2.unified_ast_dump


def test_add_type_annotation():
    c1 = """
    def foo(a):
        b = 0
        return str(a + b)
    """

    c2 = """
    def foo(a: int) -> str:
        b: float = 0
        return str(a + b)
    """

    assert_ast_eq(c1, c2)


def test_change_function_name():

    c1 = """
    def foo():
        return
    """

    c2 = """
    def bar():
        return
    """

    assert_ast_eq(c1, c2)


def test_change_argument_name():

    c1 = """
    def foo(a):
        return a
    """

    c2 = """
    def foo(b):
        return b
    """

    assert_ast_eq(c1, c2)


def test_rename_varargs():
    c1 = """
    def foo(*args):
        return args
    """

    c2 = """
    def foo(*a):
        return a
    """

    assert_ast_eq(c1, c2)


def test_rename_varargs():
    c1 = """
    def foo(**kwargs):
        return kwargs
    """

    c2 = """
    def foo(**k):
        return k
    """

    assert_ast_eq(c1, c2)


def test_change_default_argument_name():

    c1 = """
    def foo(a=1):
        return a
    """

    c2 = """
    def foo(b=1):
        return b
    """

    assert_ast_eq(c1, c2)


def test_change_default_argument_value():

    c1 = """
    def foo(a=1):
        return a
    """

    c2 = """
    def foo(a=2):
        return a
    """

    assert_ast_eq(c1, c2)


def test_swap_argument_order():

    c1 = """
    def foo(a, b):
        return a - b
    """

    c2 = """
    def foo(b, a):
        return a - b
    """

    assert_ast_eq(c1, c2)


def test_rename_local_variable():
    c1 = """
    def foo():
        a = 1
        return a
    """

    c2 = """
    def foo():
        b = 1
        return b
    """

    assert_ast_eq(c1, c2)


def test_rename_global_variable():
    c1 = """
    def foo():
        return global_var1
    """

    c2 = """
    def foo():
        return global_var2
    """

    assert_ast_eq(c1, c2)


def test_aug_assign():
    c1 = """
    def foo():
        a = 1
        a += 1
        return a
    """

    c2 = """
    def foo():
        a = 1
        a = a + 1
        return a
    """

    assert_ast_eq(c1, c2)


def test_complex_aug_assign():
    c1 = """
    def foo(a):
        a.b["c"] += a.d["e"]
    """

    c2 = """
    def foo(a):
        a.b["c"] = a.b["c"] + a.d["e"]
    """

    assert_ast_eq(c1, c2)

def test_equivalent_internal_lambda_logic():
    c1 = """
    def foo(a):
        f = lambda x: x + 1
        return f(a)
    """

    c2 = """
    def foo(a):
        f = lambda n: n + 1
        return f(a)
    """

    assert_ast_eq(c1, c2)

def test_async_function_def():
    c1 = """
    async def foo():
        pass
    """

    c2 = """
    async def bar():
        pass
    """
    
    assert_ast_eq(c1, c2)

def test_assign_tuple():
    c1 = """
    def foo():
        (a1, a2) = (t1, t2)
    """

    c2 = """
    def bar():
        (x1, x2) = (t1, t2)
    """

    assert_ast_eq(c1, c2)

def test_assign_list():
    c1 = """
    def foo():
        [a1, a2] = baz
    """

    c2 = """
    def bar():
        [x1, x2] = baz
    """

    assert_ast_eq(c1, c2)

def test_assign_starred():
    c1 = """
    def foo():
        [a1, *a2] = baz
    """

    c2 = """
    def bar():
        [x1, *x2] = baz
    """

    assert_ast_eq(c1, c2)