from checkpointing.identifier.func_call.hash import AutoHashIdentifier
from checkpointing.identifier.func_call.context import FuncCallContext


def assert_id_eq(c1: FuncCallContext, c2: FuncCallContext):
    ahi = AutoHashIdentifier(unify_code=True)
    assert ahi.identify(c1) == ahi.identify(c2)


def test_rename_function():
    def foo():
        return

    def bar():
        return

    c1 = FuncCallContext(foo, (), {})
    c2 = FuncCallContext(bar, (), {})

    assert_id_eq(c1, c2)


def test_change_argument_default_value_but_apply_same_value():
    def foo(a=1):
        return a

    def bar(a=2):
        return a

    c1 = FuncCallContext(foo, (), {})
    c2 = FuncCallContext(bar, (1,), {})

    assert_id_eq(c1, c2)


def test_change_argument_name():
    def foo(a):
        return a

    def bar(b):
        return b

    c1 = FuncCallContext(foo, (1,), {})
    c2 = FuncCallContext(bar, (1,), {})

    assert_id_eq(c1, c2)


def test_swap_argument_order():
    def foo(a, b):
        return a - b

    def bar(b, a):
        return a - b

    c1 = FuncCallContext(foo, (1, 2), {})
    c2 = FuncCallContext(bar, (2, 1), {})

    assert_id_eq(c1, c2)
