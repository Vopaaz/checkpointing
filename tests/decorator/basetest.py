from checkpointing.decorator.base import Context, DecoratorCheckpoint


class DummyDecoratorCheckpoint(DecoratorCheckpoint):
    """
    A concrete DecoratorCheckpoint with dummy implementation of retrieve and save.
    """

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

    assert Context((1, 2), {"arg3": 3, "arg4": 4}, foo).arguments == expected
    assert Context((1, 2), {"arg3": 3, "arg4": 4, "arg5": 5}, foo).arguments == expected
    assert Context((1, 2, 3, 4, 5), {}, foo).arguments == expected

    decorated_foo(1, 2, 3, 4, 5)
    assert deco.context.arguments == expected

    decorated_foo(arg1=1, arg2=2, arg3=3, arg4=4)
    assert deco.context.arguments == expected

    decorated_foo(1, 2, 3, arg4=4, arg5=5)
    assert deco.context.arguments == expected

    expected["arg5"] = 6
    decorated_foo(1, 2, 3, 4, arg5=6)
    assert deco.context.arguments == expected

    decorated_foo(1, 2, 3, 4, 6)
    assert deco.context.arguments == expected

    decorated_foo(1, 2, 3, 4, 6, 6)
    assert deco.context.arguments == expected
