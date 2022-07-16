from checkpointing.identifier.func_call.context import FuncCallContext
from checkpointing.identifier import AutoHashIdentifier
from checkpointing.exceptions import GlobalStatementError, NonlocalStatementError
from pytest import raises

x = 0


def test_global_statement_leads_to_error():
    def foo():
        global x

    with raises(GlobalStatementError):
        AutoHashIdentifier().identify(FuncCallContext(foo, (), {}))

def test_nonlocal_statement_leads_to_error():

    x = 1

    def foo():
        nonlocal x

    with raises(NonlocalStatementError):
        AutoHashIdentifier().identify(FuncCallContext(foo, (), {}))
