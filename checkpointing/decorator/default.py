from checkpointing.decorator.base import HashDecoratorCheckpoint


def checkpoint():
    # TODO: Add parameters
    return DefaultDecoratorCheckpoint()


class DefaultDecoratorCheckpoint(HashDecoratorCheckpoint):
    pass
