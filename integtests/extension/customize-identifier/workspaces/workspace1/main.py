from checkpointing import (
    DecoratorCheckpoint, 
    FuncCallIdentifierBase, 
    PickleFileCache
)

class FuncNameIdentifier(FuncCallIdentifierBase):
    def identify(self, context):
        return context.name

@DecoratorCheckpoint(FuncNameIdentifier(), PickleFileCache())
def foo():
    print("Running")
    return 1

if __name__ == "__main__":
    print(foo())
    