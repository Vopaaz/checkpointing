# Use Cases

This page introduces when the "checkpointed" function will be skipped by retrieving the cached value,
and when will it re-execute.

- [Cases when the function is skipped](#cases-when-the-function-is-skipped)
    - [Refactor](#refactor)
- [Cases when function is re-executed](#cases-when-function-is-re-executed)

!!! attention
    All cases mentioned in this page leads to the correct result.
    However, there are some cases where the function will be incorrectly skipped,
    or not using the cache as expected.
    Please see [Known Caveats](caveats.md) page.

## Cases when the function is skipped

### Refactor

None of the following code changes will cause the function to rerun:

- Renaming global/local variables, arguments
- Adding type annotations and comments
- Reformat the code

For example, after running the following script:

```python
from checkpointing import checkpoint

N = 0

@checkpoint()
def foo(a):
    print("Running")
    b = a + N
    return b

if __name__ == "__main__":
    print(foo(1))
```

Change the script file to:

```python
from checkpointing import checkpoint

X = 0 # Global variable is renamed


@checkpoint()
def foo(t: int) -> int: # Argument is renamed and type annotation is added
    print("Running")
    result = t + X
    return result # However, the code logic does not change


if __name__ == "__main__":
    print(foo(1))
```



## Cases when function is re-executed