# Behavior on Code Change

This page describes the cases where the checkpointed function could be correctly skipped by retrieving the cached value,
and cases where it would be correctly re-executed.

!!! attention
    All examples in this page leads to the correct result.
    However, there are some cases where the function will be incorrectly skipped,
    or not using the cache as expected.
    Please see [Known Caveats](caveats.md) page.

## Skipped cases

### Renaming function arguments

After executing the following script,

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a):
    print("Running")
    return a

if __name__ == "__main__":
    foo(1)
```

Rename the function argument:


```python
from checkpointing import checkpoint

@checkpoint()
def foo(x):
    print("Running")
    return x

if __name__ == "__main__":
    foo(1)
```

When executing the modified script,
`foo` will be skipped as the checkpoint figured that the code change is only about renaming function arguments.
The result will be retrieved from the cache.

### Renaming global/local variables

After executing the following script,

```python
from checkpointing import checkpoint

N = 0

@checkpoint()
def foo():
    print("Running")
    b = N + 1
    return b

if __name__ == "__main__":
    print(foo())
```

Rename the reference global variable and the local variable:

```python
from checkpointing import checkpoint

X = 0

@checkpoint()
def foo():
    print("Running")
    z = X + 1
    return z

if __name__ == "__main__":
    print(foo())
```

When executing the modified script,
`foo` will be skipped as the checkpoint figured that the code change is only about renaming those variables.
The result will be retrieved from the cache.


### Renaming the function


After executing the following script,

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a):
    print("Running")
    return a

if __name__ == "__main__":
    print(foo(1))
```

Rename the function to `bar`:

```python
from checkpointing import checkpoint

@checkpoint()
def bar(a):
    print("Running")
    return a

if __name__ == "__main__":
    print(bar(1))
```

When executing the modified script,
`bar` will be skipped as the checkpoint figured that its logic is the same as the earlier `foo`.
The result will be retrieved from the cache.

### Adding comments and type annotations

After executing the following script,

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a):
    print("Running")
    return a

if __name__ == "__main__":
    print(foo(1))
```

Add comments and annotations:

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a: int) -> int:
    print("Running")
    return a  # Add some comments

if __name__ == "__main__":
    print(foo(1))
```

When executing the modified script,
`foo` will be skipped as the checkpoint figured that it's only adding type annotations and comments.
The result will be retrieved from the cache.

### Changing argument default value

After executing the following script,

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a = 1):
    print("Running")
    return a

if __name__ == "__main__":
    print(foo())
```

Change the default value of argument `a`,
but when calling `foo`, plug in the previously used value:

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a = 2):
    print("Running")
    return a

if __name__ == "__main__":
    print(foo(1))
```

When executing the modified script, `foo` will be skipped as the checkpoint figured that the actual value of `a` is `1` in both executions. 
The result will be retrieved from the cache.

This also works if you remove or add default value to an argument.
In short - checkpoint does not care about the defaults,
it only consider what values are actually plugged in.


## Re-executed cases

### Changing code logic

After executing the following script,

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a):
    print("Running")
    return a + 1

if __name__ == "__main__":
    print(foo(0))
```

Change the `+` to `-`,

```python
from checkpointing import checkpoint

@checkpoint()
def foo(a):
    print("Running")
    return a - 1

if __name__ == "__main__":
    print(foo(0))
```

When executing the modified script, `foo` will be re-executed and return the correct result, `-1`,
because checkpoint finds that the actual code logic of `foo` has changed.

### Passing different parameters







