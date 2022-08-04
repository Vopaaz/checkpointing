## Introduction

The checkpoint can be extended to store the cache not as a pickle file
(e.g., for sharing among a group of coworkers),
or ignore/consider some additional aspects of the function call context.

To do so, we need to briefly introduce how the `checkpoint` decorator works.

The `checkpoint` decorator is actually a shortcut for creating a 
[`DecoratorCheckpoint`](./apidoc/checkpointing/decorator/base.html){:target="_blank"},
which receives the following objects as parameters[^1] and coordinate them:

- An identifier that creates an ID for any function call context:
    [`AutoFuncCallIdentifier`](./apidoc/checkpointing/identifier/func_call/auto.html){:target="_blank"}
- A cache that saves and retrieves the return value with a given ID,
    or reports that the ID hasn't been saved before:
    [`PickleFileCache`](./apidoc/checkpointing/cache/pickle_file.html){:target="_blank"}

[^1]: It also receives other parameters that controls high-level behaviors, such as `on_error`

Therefore,

- If you want to control how the checkpoint determines whether to rerun the function,
you need to implement your identifier.
- If you want to change how the function return values are saved, you need to implement your cache.

Finally, decorate the function with `@DecoratorCheckpoint(identifier, cache)`

!!! example

    ```python
    from checkpointing import DecoratorCheckpoint, AutoFuncCallIdentifier, PickleFileCache

    class CustomizedCache:
        ... # Your implementation, see below

    class CustomizedIdentifier:
        ... # Your implementation, see below

    # If you only want to change how the results are saved
    @DecoratorCheckpoint(AutoFuncCallIdentifier(), CustomizedCache()) 
    def foo():
        return 0

    # If you only want to change how re-execution is determined
    @DecoratorCheckpoint(CustomizedIdentifier(), PickleFileCache()) 
    def bar():
        return 0

    # If you want to combine both
    @DecoratorCheckpoint(CustomizedIdentifier(), CustomizedCache()) 
    def qux():
        return 0
    ```


## Customize an identifier

The identifier should implement the 
[`FuncCallIdentifierBase`](./apidoc/checkpointing/identifier/func_call/base.html){:target="_blank"}
interface, 
in particular the `identify` method.


The `identify` method accepts one argument of the
[`FuncCallContext`](./apidoc/checkpointing/identifier/func_call/context.html){:target="_blank"}
type,
and returns a `ContextId`.
Please follow the link to see what attributes and methods are provided by
[`FuncCallContext`](./apidoc/checkpointing/identifier/func_call/context.html){:target="_blank"}.

The `ContextId` can be any data type,
as long as it is in accordance with the cache that will be used together.
If you use the built-in `PickleFileCache`,
the returned ID should be a string that can be used as a valid file name.


Here is an example of the implementation and usage of an identifier that
only uses the function name as the `ContextId`.

```python
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
    return 0
```

As a result, the function `foo` will only rerun if it's renamed.


## Customize a cache

The cache should inherit the
[`CacheBase`](./apidoc/checkpointing/cache/base.html){:target="_blank"}
abstract class,
and implement the `save` and `retrieve` method.

The `save` method accepts two arguments,
(1) the `ContextId` produced by identifier,
(2) the result of the checkpointed function.

The `retrieve` method takes a `ContextId` as the argument, and

- returns the previously saved result, if it exists
- raises an `CheckpointNotExist` special error, otherwise

The data type of `ContextId` is determined by the identifier you use.
If you use the built-in `AutoFuncCallIdentifier`, 
it will be a 
[`hexdigest`](https://docs.python.org/3/library/hashlib.html#hashlib.hash.hexdigest){:target="_blank"}
string.

Here is an example of the implementation and usage of a cache that simply
wraps the built-in dictionary.

```python
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
def foo():
    return 0
```

As a result, the return value will only be cached in the dict in the memory.



