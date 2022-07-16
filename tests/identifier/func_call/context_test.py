import inspect
from checkpointing.identifier.func_call.context import FuncCallContext


def test_get_nonlocal_variable_with_local_variable_of_outer_frame():
    def foo():
        pass

    x = 1

    ctx = FuncCallContext(foo, (), {}, inspect.currentframe())
    assert ctx.get_nonlocal_variable("x") == 1


globvar = 2


def test_get_nonlocal_variable_with_global_variable():
    def foo():
        pass

    ctx = FuncCallContext(foo, (), {}, inspect.currentframe())
    assert ctx.get_nonlocal_variable("globvar") == 2

testvar = 1

def test_get_nonlocal_variable_prioritize_local_variable_of_outer_frame_over_global_variable():
    def foo():
        pass

    testvar = 2

    ctx = FuncCallContext(foo, (), {}, inspect.currentframe())
    assert ctx.get_nonlocal_variable("testvar") == 2


def test_get_nonlocal_variable_without_frame():
    def foo():
        pass

    ctx = FuncCallContext(foo, (), {})
    assert ctx.get_nonlocal_variable("anyvar") is None


def test_get_nonlocal_variable_that_does_not_exist():
    def foo():
        pass

    ctx = FuncCallContext(foo, (), {}, inspect.currentframe())
    assert ctx.get_nonlocal_variable("anyvar") is None
