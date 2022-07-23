This page introduces the cases where you would expect the function to be re-executed,
but it's actually skipped by checkpointing, or the vice versa.
We would also give suggestions on how to avoid those cases.


??? info "How the cases are written"

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

## Falsely skipped cases

### Reference function logic change

checkpointing only watches the code change of the decorated function itself.
Any reference function are only identified by their reference,
while the change of code logic cannot be captured.

=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    def bar(x):
        return x

    @checkpoint()
    def foo(x):
        return bar(x)

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    def bar(x):
        return x + 1

    @checkpoint()
    def foo(x):
        return bar(x)

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    0
    ```

Unfortunately the change in `bar` is not captured, resulting in a wrong return value.

We suggest to decouple your code logic, 
such that the checkpointed function only invoke other functions that are known to be "static",
e.g. those from an external library.
Instead of invoking another custom function whose logic is likely to change in the future,
pass its result as an argument.

```python title="script.py"
from checkpointing import checkpoint

def bar(x):
    return x + 1

@checkpoint()
def foo(x):
    return x

if __name__ == "__main__":
    x = 0
    y = bar(x) # The change in `bar` can be reflected by y, 
    z = foo(y) # and thus can be correctly captured by `foo`
```


### Object method logic change

The object method is identified by its name only.
Change in the object method code cannot be captured by the checkpoint.


=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    class Bar:
        def __init__(self) -> None:
            self.x = 0

        def baz(self):
            self.x += 1

    @checkpoint()
    def foo(bar):
        bar.baz()
        return bar

    if __name__ == "__main__":
        bar = Bar()
        result = foo(bar)
        print(result.x)
    ```

    ```text title="Output"
    1
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    class Bar:
        def __init__(self) -> None:
            self.x = 0

        def baz(self):
            pass

    @checkpoint()
    def foo(bar):
        bar.baz()
        return bar

    if __name__ == "__main__":
        bar = Bar()
        result = foo(bar)
        print(result.x)
    ```

    ```text title="Output"
    1
    ```

Unfortunately the change in `Bar.baz` is not captured, resulting in a wrong return value.

We suggest to only use objects, such that the checkpointed function only invoke other functions that are known to be "static", e.g. those from an external library.
