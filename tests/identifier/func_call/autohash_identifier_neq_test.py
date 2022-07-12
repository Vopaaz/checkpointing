from checkpointing.identifier.func_call.hash import AutoHashIdentifier
from checkpointing.identifier.func_call.context import FuncCallContext


def assert_context_neq(c1: FuncCallContext, c2: FuncCallContext):
    ahi = AutoHashIdentifier(unify_code=True)
    assert ahi.identify(c1) != ahi.identify(c2)

