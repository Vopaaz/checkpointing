
This page describes the cases where the checkpointed function could be correctly skipped by retrieving the cached value,
and cases where it would be correctly re-executed.

!!! attention
    All examples in this page leads to the correct result.
    However, there are some cases where the function will be incorrectly skipped,
    or not using the cache as expected.
    Please see [Caveats](caveats.md).

???+ info "How the cases are written"

    The cases are generally written in the following format of two tabs.

    === "1st run"

        ```python title="script.py"
        def foo():
            print("Output before the code change")

        if __name__ == "__main__":
            foo()
        ```

        ```text title="Output"
        Output before the code change
        ```

    === "2nd run"

        ```python title="script.py"
        def foo():
            print("Output after the code change")

        if __name__ == "__main__":
            foo()
        ```

        ```text title="Output"
        Output after the code change
        ```

    This denotes:

    - At first, you have the script in the "1st run" tab.
      Running it gives you the corresponding output.
    - Next you modify the script and change it to what's shown in the "2nd run" tab.
      Running it gives you another result,
      and it shows how the function gets skipped or re-executed.


## Skipped cases

### Renaming parameters

=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a

    if __name__ == "__main__":
        foo(1)
    ```

    ```text title="Output"
    Running
    1
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(x):
        print("Running")
        return x

    if __name__ == "__main__":
        foo(1)
    ```

    ```text title="Output"
    1
    ```

When executing the modified script,
`foo` will be skipped as the checkpoint figured that the code change is only about renaming function parameters.
The result will be retrieved from the cache.

### Renaming variables

=== "1st run"

    ```python title="script.py"
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

    ```text title="Output"
    Running
    1
    ```

=== "2nd run"

    ```python title="script.py"
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

    ```text title="Output"
    1
    ```

When executing the modified script,
`foo` will be skipped as the checkpoint figured that the code change is only about renaming those variables.
The result will be retrieved from the cache.


### Renaming the function

=== "1st run"


    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo(1))
    ```

    ```text title="Output"
    Running
    1
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def bar(a):
        print("Running")
        return a

    if __name__ == "__main__":
        print(bar(1))
    ```

    ```text title="Output"
    Running
    1
    ```

When executing the modified script,
`bar` will be skipped as the checkpoint figured that its logic is the same as the earlier `foo`.
The result will be retrieved from the cache.

### Adding comments and type annotations

=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo(1))
    ```

    ```text title="Output"
    Running
    1
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a: int) -> int:
        print("Running")
        return a  # Add some comments

    if __name__ == "__main__":
        print(foo(1))
    ```

    ```text title="Output"
    1
    ```

When executing the modified script,
`foo` will be skipped as the checkpoint figured that it's only adding type annotations and comments.
The result will be retrieved from the cache.

### Changing default values


=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a = 1):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    Running 
    1
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a = 2):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo(1))
    ```

    ```text title="Output"
    1
    ```

When executing the modified script, `foo` will be skipped as the checkpoint figured that the actual value of `a` is `1` in both executions.
The result will be retrieved from the cache.

This also works if you remove or add default value to a parameter.
In short - checkpoint does not care about the defaults,
it only consider what arguments are actually plugged in.

### Changing value of irrelevant global variables


=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    X = 0

    @checkpoint()
    def foo():
        print("Running")
        return 0

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    Running
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    X = 1

    @checkpoint()
    def foo():
        print("Running")
        return 0

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    0
    ```


When executing the modified script, `foo` will be skipped as the checkpoint figured that `X` is not referenced in the function code,
although its value has changed.



## Re-executed cases

### Changing arguments

=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    Running
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo(1))
    ```

    ```text title="Output"
    Running
    1
    ```

When executing the modified script, `foo` will be re-executed and return the correct result, `1`,
because checkpoint finds that the passed arguments are different.

### Changing code logic

=== "1st run"


    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    Running
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(a):
        print("Running")
        return a + 1

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    Running
    1
    ```

When executing the modified script, `foo` will be re-executed and return the correct result, `-1`,
because checkpoint finds that the actual code logic of `foo` has changed.


### Changing value of reference global variables

=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    X = 0

    @checkpoint()
    def foo():
        print("Running")
        return X

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    Running
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    X = 1

    @checkpoint()
    def foo():
        print("Running")
        return X

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    Running
    1
    ```

When executing the modified script, 
foo will be re-executed and return the correct result, `1`, 
because checkpoint finds that the value of a reference global variable has been modified.









