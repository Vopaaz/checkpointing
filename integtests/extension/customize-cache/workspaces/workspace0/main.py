from checkpointing import (
    DecoratorCheckpoint,
    CacheBase,
    AutoFuncCallIdentifier,
    CheckpointNotExist
)

class DictCache(CacheBase):
    def __init__(self):
        self.d = {}

    def save(self, context_id, result):
        self.d[context_id] = result

    def retrieve(self, context_id):
        if context_id not in self.d:
            raise CheckpointNotExist
        else:
            return self.d[context_id]

@DecoratorCheckpoint(AutoFuncCallIdentifier(), DictCache())
def foo(a):
    print("Running")
    return a


if __name__ == "__main__":
    print(foo(0))
    print(foo(0))
    print(foo(1))
