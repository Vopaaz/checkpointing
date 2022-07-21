# Use Cases

This page describes different cases when the "checkpointed" function will be skipped by retrieving the cached value,
and when will it re-execute.

- [Cases when the function is skipped](#cases-when-the-function-is-skipped)
    - [Renaming function arguments](#renaming-function-arguments)
    - [Renaming global/local variables](#renaming-globallocal-variables)
    - [Renaming the function](#renaming-the-function)
    - [Adding comments and type annotations](#adding-comments-and-type-annotations)
- [Cases when function is re-executed](#cases-when-function-is-re-executed)

!!! attention
    All cases mentioned in this page leads to the correct result.
    However, there are some cases where the function will be incorrectly skipped,
    or not using the cache as expected.
    Please see [Known Caveats](caveats.md) page.

## Cases when the function is skipped

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


## Cases when function is re-executed


