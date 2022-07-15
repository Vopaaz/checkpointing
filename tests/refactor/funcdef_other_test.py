from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from pytest import raises

def test_unifier_detects_global_statement():
    code = """
    def foo():
        global a
    """

    assert FunctionDefinitionUnifier(code).has_global_statement


def test_unifier_detects_nonlocal_statement():
    code = """
    def foo():
        nonlocal a
    """

    assert FunctionDefinitionUnifier(code).has_nonlocal_statement

def test_unifider_does_not_false_positive_global_nonlocal_statement():
    code = """
    def foo():
        s = "global a"
        s = "nonlocal b"
    """

    assert not FunctionDefinitionUnifier(code).has_global_statement
    assert not FunctionDefinitionUnifier(code).has_nonlocal_statement