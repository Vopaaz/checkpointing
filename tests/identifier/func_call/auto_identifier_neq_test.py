from checkpointing.identifier.func_call.auto import AutoFuncCallIdentifier
from checkpointing.identifier.func_call.context import FuncCallContext
import inspect


def assert_id_neq(c1: FuncCallContext, c2: FuncCallContext):
    ahi = AutoFuncCallIdentifier()
    assert ahi.identify(c1) != ahi.identify(c2)

def test_change_argument_default_value():
    def foo(a=1):
        return a

    def bar(a=2):
        return a

    c1 = FuncCallContext(foo, (), {})
    c2 = FuncCallContext(bar, (), {})

    assert_id_neq(c1, c2)

def test_apply_argument_different_value():
    def foo(a):
        return a

    def bar(a):
        return a

    c1 = FuncCallContext(foo, (1,), {})
    c2 = FuncCallContext(bar, (2,), {})

    assert_id_neq(c1, c2)

def test_code_different_logic():
    def foo(a):
        return a + 1

    def bar(a):
        return a - 1

    c1 = FuncCallContext(foo, (1,), {})
    c2 = FuncCallContext(bar, (2,), {})

    assert_id_neq(c1, c2)

def test_swap_argument_order_but_apply_different_logic():
    def foo(a, b):
        return a - b

    def bar(b, a):
        return b - a

    c1 = FuncCallContext(foo, (1, 2), {})
    c2 = FuncCallContext(bar, (2, 1), {})

    assert_id_neq(c1, c2)

def test_add_varargs():
    def foo(a):
        return a

    def bar(a, *b):
        return a

    c1 = FuncCallContext(foo, (1,), {})
    c2 = FuncCallContext(bar, (2,), {})

    assert_id_neq(c1, c2)


def test_add_kwargs():
    def foo(a):
        return a

    def bar(a, **b):
        return a

    c1 = FuncCallContext(foo, (1,), {})
    c2 = FuncCallContext(bar, (2,), {})

    assert_id_neq(c1, c2)

def test_referencing_changed_global_variable():

    a = 0

    def foo():
        return a

    c1 = FuncCallContext(foo, (), {}, inspect.currentframe())

    a = 1

    c2 = FuncCallContext(foo, (), {}, inspect.currentframe())

    assert_id_neq(c1, c2)


def test_referencing_different_other_function():

    def foz():
        return

    def baz():
        return

    def foo():
        return foz()

    def bar():
        return baz()

    c1 = FuncCallContext(foo, (), {}, inspect.currentframe())
    c2 = FuncCallContext(bar, (), {}, inspect.currentframe())

    assert_id_neq(c1, c2)


def test_internal_lambda_referecing_different_global_variable_with_same_name():

    a = 0

    def foo(t):
        f = lambda x: x + a
        return f(t)

    c1 = FuncCallContext(foo, (0,), {}, inspect.currentframe())

    a = 1

    def bar(t):
        f = lambda x: x + a
        return f(t)

    c2 = FuncCallContext(bar, (0,), {}, inspect.currentframe())

    assert_id_neq(c1, c2)
