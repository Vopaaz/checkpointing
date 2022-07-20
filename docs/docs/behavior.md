# Use Cases

This page describes different cases when the "checkpointed" function will be skipped by retrieving the cached value,
and when will it re-execute.

- [Cases when the function is skipped](#cases-when-the-function-is-skipped)
    - [Renaming function arguments and global/local variables](#renaming-function-arguments-and-globallocal-variables)
    - [Renaming the function](#renaming-the-function)
- [Cases when function is re-executed](#cases-when-function-is-re-executed)

!!! attention
    All cases mentioned in this page leads to the correct result.
    However, there are some cases where the function will be incorrectly skipped,
    or not using the cache as expected.
    Please see [Known Caveats](caveats.md) page.

## Cases when the function is skipped

### Renaming function arguments and global/local variables

After executing the following script,

```python
from checkpointing import checkpoint

N = 0

@checkpoint()
def foo(a):
    print("Running")
    b = a + N
    return b

if __name__ == "__main__":
    foo(1)
```

Rename the function arguments and global/local variables:


```python
from checkpointing import checkpoint

X = 0

@checkpoint()
def foo(t):
    print("Running")
    z = t + X
    return z

if __name__ == "__main__":
    foo(1)
```

`foo` will be skipped as the checkpoint figured that the code change is only about renaming variables.
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

Rename the function to `bar`, so it becomes

```python
from checkpointing import checkpoint

@checkpoint()
def bar(a):
    print("Running")
    return a

if __name__ == "__main__":
    print(bar(1))
```



## Cases when function is re-executed


