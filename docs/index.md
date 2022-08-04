# Welcome to checkpointing

Persistent cache for Python functions.

## Introduction

`checkpointing` provides a decorator which allows you to cache the return value of a
[pure function](https://en.wikipedia.org/wiki/Pure_function#Compiler_optimizations)[^1],
by default as a pickle file on the disk.
When the function is called later with the same arguments, it automatically skips the function execution,
retrieves the cached value and return.


[^1]: We take the alternative definition of the "pure function", meaning that it only has property 2:
"the function has no side effects (no mutation of local static variables, non-local variables,
mutable reference arguments or input/output streams)".
We do allow the return value to vary due to changes in non-local variables and other factors,
as it's often the case in project development.



For example,

```python
from checkpointing import checkpoint

@checkpoint()
def calc(a, b):
    print(f"calc is running for {a}, {b}")
    return a + b

if __name__ == "__main__":
    result = calc(1, 2)
    print(f"result: {result}")
```

Run this script, and the output will be

```text
calc is running for 1, 2
result: 3
```

Now the return value has been cached, and if you rerun this script, the output will be

```text
result: 3
```

The execution of `calc` is skipped, but the result value is retrieved from the disk and returned as expected.

However, if the function call context has changed, the function will be re-executed and return the new value.
For example,

- if it is passed with different arguments, e.g. `calc(1, 3)`, `calc` would rerun and return `4`
- if the code logic has changed, e.g. `return a - b`, `calc` would rerun and return `-1`

The `checkpoint` has a built-in wise strategy to decide when it needs or doesn't need to re-execute the function.
More details are discussed in [Behavior on Code Change](behavior.md).
This is also the main advantage of `checkpointing` compared to other similar packages,
see [Comparison with similar packages](comparison.md).

!!! attention
    However, there are some cases where the checkpoint cannot correctly make the rerun decision.
    Please read through the [Caveats](caveats.md) page and avoid those patterns.

Although the package focuses on persisting the cache across different executions,
it also works if you call the same function multiple times within one execution.


### Use cases

The built-in `checkpoint` is designed for projects that

- runs in a local development environment
- involves repeatedly executing long-running
[pure functions](https://en.wikipedia.org/wiki/Pure_function#Compiler_optimizations)[^1]
on the same set of arguments
- are somewhat "experimental", so it involves a lot of code changes back and forth

For example, such use cases are very common in the preliminary stage of machine learning projects.


## Installation

This package is available on [PyPI](https://pypi.org/project/checkpointing/), and can be installed with `pip`.

```shell
$ pip install checkpointing
```

## Basic usage

### Create a checkpoint

Import the `checkpoint` from this package and use it as the decorator of a function
(notice the `()` after `checkpoint`)

```python
from checkpointing import checkpoint

@checkpoint()
def foo():
    return 0
```

After that, `foo` will be automatically cached, skipped,
or re-executed as described previously.
You can call `foo` in the same way as you normally would.

### Configure the checkpoint

#### Cache directory

By default, the results are saved as pickle files in `./.checkpointing/`,
if you want to store them elsewhere, you can do

```python
@checkpoint(directory="other_dir")
```

#### Behavior on internal error

During the execution, there could be unexpected errors within the checkpoint.
When this happens, the default behavior is to give you a warning,
and just rerun the function without the caching stuff.
This ensures that your code won't fail because of using this package.
However, you can change this behavior with the `on_error` option.

```python
@checkpoint(on_error="raise")
```

This will terminate the function call and raise the internal error.

```python
@checkpoint(on_error="ignore")
```

This will rerun the function when an internal error occurs without raising any warning.


#### Pickle protocol

The function return value will be saved with the built-in [pickle](https://docs.python.org/3/library/pickle.html) module.
We use [protocol 5](https://peps.python.org/pep-0574/) by default for all Python versions,
in favor of its ability to efficiently handle large data. [^2]
However, if you want to change the protocol, you could use the `cache_pickle_protocol` option.

[^2]: For Python 3.7, we use the backport [pickle5](https://pypi.org/project/pickle5/) package to support it.

```python
import pickle

@checkpoint(cache_pickle_protocol=pickle.DEFAULT_PROTOCOL)
```

!!! warning

    Using protocol earlier than 5 will cause significantly more memory when saving large data objects.


#### Global setting

By modifying a global dictionary, you can change the configurations for all checkpoints.

```python
from checkpointing import defaults
import pickle

defaults["cache.filesystem.directory"] = "other_dir"
defaults["checkpoint.on_error"] = "ignore"
defaults["cache.pickle_protocol"] = pickle.DEFAULT_PROTOCOL
```

Please set this at the top level of your module/script, before you create any `checkpoint`.

#### Further customization

If you want more flexibility, such as storing the cache not as a pickle file,
or ignore/consider some additional aspects of the function call context,
please see [Extending the Checkpoint](extension.md) for details.


### Force rerun a checkpoint

You can force rerun a checkpointed function with

```python
foo.rerun(arg)
```

where `foo` is the decorated function.
This would be equivalent to directly invoking `foo(arg)`.
The return value of this rerun will be cached to the disk and overwrite the previous one, if it exists.

This is useful if some factors that would affect the function return value have changed,
but `checkpoint` failed to capture this difference, as described in the [Caveats](caveats.md).

## Usage notes

Please be aware that

- Since the function will be skipped if it was cached before, user shouldn't mutate an argument in the function body
  (as required by the definition of pure function)
- If the project involves randomness, it's the user's responsibility to set the random seed or random state,
  such that the arguments and reference global variables of the cached function are identical
- The built-in strategy to determine if a function needs to be re-executed is imperfect.
  Please see [Caveats](caveats.md),
  and avoid those cases when the rerun condition cannot be correctly determined.

