from checkpointing.exceptions import ExpensiveOverheadWarning, CheckpointNotExist, CheckpointFailedError, CheckpointFailedWarning
from checkpointing.decorator.base import Context, DecoratorCheckpoint
from warnings import catch_warnings
from time import sleep


class DummyDecoratorCheckpoint(DecoratorCheckpoint):
    def retrieve(self, ctx: Context):
        return None

    def save(self, ctx: Context, result) -> None:
        pass


deco = DummyDecoratorCheckpoint()


def foo(arg1, arg2, arg3, arg4, arg5=5, arg6=6):
    pass


@deco
def decorated_foo(arg1, arg2, arg3, arg4, arg5=5, arg6=6):
    pass


def test_context_compiles_correct_arguments():
    expected = {f"arg{i}": i for i in range(1, 7)}

    assert Context(foo, (1, 2), {"arg3": 3, "arg4": 4}).arguments == expected
    assert Context(foo, (1, 2), {"arg3": 3, "arg4": 4, "arg5": 5}).arguments == expected
    assert Context(foo, (1, 2, 3, 4, 5), {}).arguments == expected

    decorated_foo(1, 2, 3, 4, 5)
    assert deco._DecoratorCheckpoint__context.arguments == expected

    decorated_foo(arg1=1, arg2=2, arg3=3, arg4=4)
    assert deco._DecoratorCheckpoint__context.arguments == expected

    decorated_foo(1, 2, 3, arg4=4, arg5=5)
    assert deco._DecoratorCheckpoint__context.arguments == expected

    expected["arg5"] = 6
    decorated_foo(1, 2, 3, 4, arg5=6)
    assert deco._DecoratorCheckpoint__context.arguments == expected

    decorated_foo(1, 2, 3, 4, 6)
    assert deco._DecoratorCheckpoint__context.arguments == expected

    decorated_foo(1, 2, 3, 4, 6, 6)
    assert deco._DecoratorCheckpoint__context.arguments == expected


class SlowRetrievalDecoratorCheckpoint(DecoratorCheckpoint):
    def retrieve(self, context: Context):
        sleep(0.1)
        raise CheckpointNotExist

    def save(self, context: Context, result) -> None:
        pass


@SlowRetrievalDecoratorCheckpoint()
def decorated_by_slow():
    pass


def test_raise_warning_when_overhead_larger_than_computation():
    with catch_warnings(record=True) as w:
        decorated_by_slow()

        assert len(w) == 1
        assert issubclass(w[0].category, ExpensiveOverheadWarning)


class ErroneousDecoratorCheckpoint(DecoratorCheckpoint):
    def retrieve(self, context: Context):
        raise RuntimeError

    def save(self, context: Context, result) -> None:
        pass

@ErroneousDecoratorCheckpoint(error="raise")
def decorated_by_raise():
    pass

@ErroneousDecoratorCheckpoint(error="warn")
def decorated_by_warn():
    pass

@ErroneousDecoratorCheckpoint(error="ignore")
def decorated_by_ignore():
    pass


def test_deal_with_error_according_to_error_args():
    failed = False
    try:
        decorated_by_raise()
    except RuntimeError:
        failed = True

    assert failed

    with catch_warnings(record=True) as w:
        decorated_by_warn()

        assert len(w) == 1
        assert issubclass(w[0].category, CheckpointFailedWarning)

    with catch_warnings(record=True) as w:
        decorated_by_ignore()

        assert len(w) == 0
