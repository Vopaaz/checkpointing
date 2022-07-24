# Comparison with Similar Packages

Some other packages have similar functionality as `checkpointing`.
However, we handle some cases better than them, as explained below.


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

    - First, you have the script in the "1st run" tab.
      Running it gives you the corresponding output.
    - Next, modify the script and change it to what's shown in the "2nd run" tab.
      Running it gives you another result,
      and it shows how the function gets skipped or re-executed.
    
    If you want to try it out, please remember to clear the cache directory
    (`./.checkpointing` by default) between two cases, as one case might affect another.

## cachier

The following cases are tested with
[cachier](https://github.com/shaypal5/cachier) version 1.5.4[^1].

### Code change

cachier does not watch the function code at all,
therefore, if the code logic has changed, it will not rerun, leading to erroneous results.


=== "1st run"

    ```python title="script.py"
    from cachier import cachier

    @cachier()
    def foo(x):
        return x

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from cachier import cachier

    @cachier()
    def foo(x):
        return x + 1

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    0
    ```

Even though the code is changed to `x + 1`, 
cachier is using the previously cached value, which is wrong.

Replace cachier with checkpointing, the second execution of the script will rerun `foo`,
and gives the correct result, `-1`.

### Limited hashable types

cachier can only work on minimal data types as arguments.

```python
import numpy as np
from cachier import cachier

@cachier()
def foo(x):
    return x

if __name__ == "__main__":
    df = pd.DataFrame()
    foo(df)
```

Run this script and it will raise a `TypeError`, because it cannot hash the `numpy.ndarray` object.
You will have to write your own hasher, even on this commonly used data type.

In contrast, checkpoint has built-in support for commonly used data manipulation packages,
such as numpy and pandas.

## joblib

The following cases are tested with [joblib](https://joblib.readthedocs.io/en/latest/memory.html#memory) version 1.1.0[^1].

### Irrelevant code change

joblib watches the function code source directly,
which means that even adding comments or reformatting the code will cause a function to rerun.

=== "1st run"

    ```python title="script.py"
    from joblib import Memory

    memory = Memory(".joblib", verbose=0)

    @memory.cache
    def foo():
        print(f"Running")

    if __name__ == "__main__":
        foo()
    ```

    ```text title="Output"
    Running
    ```

=== "2nd run"

    ```python title="script.py"
    from joblib import Memory

    memory = Memory(".joblib", verbose=0)

    @memory.cache
    def foo():
        # Add some comments
        print(f"Running") 

    if __name__ == "__main__":
        foo()
    ```

    ```text title="Output"
    Running
    ```

The only difference in the code is a line of comment,
which shouldn't affect the function's return value.
However, joblib failed to use the cache, causing redundant re-compute.

Replace joblib with checkpointing, in the 2nd run, `foo` won't be executed.
We watch the function code with an [AST](https://docs.python.org/3/library/ast.html)
based approach, which eliminates the effect of type annotations, comments, and formatting.

### Global variable

joblib does not consider the reference global variable.

=== "1st run"

    ```python title="script.py"
    from joblib import Memory

    memory = Memory(".joblib", verbose=0)

    a = 1

    @memory.cache
    def foo():
        return a

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    1
    ```


=== "2nd run"

    ```python title="script.py"
    from joblib import Memory

    memory = Memory(".joblib", verbose=0)

    a = 2

    @memory.cache
    def foo():
        return a

    if __name__ == "__main__":
        print(foo())
    ```

    ```text title="Output"
    1
    ```

Even though the value of the reference global variable is changed to `2`,
the execution of `foo` is skipped and the previous cache is returned, which is wrong.

Replace joblib with checkpointing, in the second execution of the script, 
`foo` will be invoked and return the correct result `2`.


[^1]: These are the latest versions as of 2022/07/18, the date when this document is written.
