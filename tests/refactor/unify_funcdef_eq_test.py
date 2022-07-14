from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from pytest import raises



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
