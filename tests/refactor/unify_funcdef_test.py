from checkpointing.refactor.unify.funcdef import FunctionDefinitionUnifier
from pytest import raises

u = FunctionDefinitionUnifier()

def test_getting_renaming_without_unify_raises_error():
    with raises(RuntimeError):
        return FunctionDefinitionUnifier().args_renaming

def test_change_argument_name():

    c1 = """
    def foo(a):
        return a
    """

    c2 = """
    def foo(b):
        return b
    """

    assert u.unify(c1) == u.unify(c2)

def test_change_default_argument_name():

    c1 = """
    def foo(a=1):
        return a
    """

    c2 = """
    def foo(b=1):
        return b
    """

    assert u.unify(c1) == u.unify(c2)

def test_change_default_argument_value():

    c1 = """
    def foo(a=1):
        return a
    """

    c2 = """
    def foo(a=2):
        return a
    """

    assert u.unify(c1) == u.unify(c2)




