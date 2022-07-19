# Comparison with similar packages

Some other packages have similar functionality as `checkpointing`.
However we handle some cases better than them, as explained below.

## cachier

The following cases are tested with
[cachier](https://github.com/shaypal5/cachier) version 1.5.4[^1].

### Code change

cachier does not watch the function code at all,
therefore, if the code logic has changed, it will not rerun which leads to wrong result.

```python
from cachier import cachier

@cachier()
def foo(x):
    return x + 1

if __name__ == "__main__":
    print(foo(0))
```

Run the above script, the result is `1`.
Then change the code to:

```python
from cachier import cachier

@cachier()
def foo(x):
    return x - 1 # Plus becomes minus

if __name__ == "__main__":
    print(foo(0))
```

Rerun the script again and the output is still `1`, which is incorrect.

Replace cachier with checkpointing, the second execution of the script will rerun `foo`,
and gives the correct result, `-1`.

### Limited hashable types

cachier can only work on very limited data types as arguments.

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
You will have to write your own hasher, even on this very commonly used data type.

In contrast, checkpoint has built-in support for commonly used data manipulation packages,
such as numpy and pandas.

## joblib

The following cases are tested with [joblib](https://joblib.readthedocs.io/en/latest/memory.html#memory) version 1.1.0[^1].

### Code change

joblib watches the function code source directly,
which means that even adding comments to the code will cause a function to rerun.

```python
from joblib import Memory

memory = Memory(".joblib", verbose=0)

@memory.cache
def foo():
    print(f"Running")

if __name__ == "__main__":
    foo()
```

Run this script and `foo` will be executed as expected.
However, after you add some comments to the function definition:

```python
from joblib import Memory

memory = Memory(".joblib", verbose=0)

@memory.cache
def foo():
    # Add some comments
    print(f"Running") 

if __name__ == "__main__":
    foo()
```

Run this script again and you will still see `Running` in the output,
which means that the function is re-executed.

Replace joblib with checkpointing, in the second execution of the script, `foo` won't be executed.
This package watches the function code with an [AST](https://docs.python.org/3/library/ast.html)
based approach, which can automatically determine that "there is no need to rerun" for some code change cases.

### Global variable

joblib does not take the referenced global variable into account.

```python
from joblib import Memory

memory = Memory(".joblib", verbose=0)

a = 1

@memory.cache
def foo():
    return a

if __name__ == "__main__":
    print(foo())
```

This gives `1` as expected. However, change the global `a` and rerun the script again:

```python
from joblib import Memory

memory = Memory(".joblib", verbose=0)

a = 2

@memory.cache
def foo():
    return a

if __name__ == "__main__":
    print(foo())
```

The execution of `foo` is skipped and the returned result is still `1`, which is wrong.

Replace joblib with checkpointing, in the second execution of the script, 
`foo` will be invoked and the correct result `2` will be returned.


[^1]: These are the latest versions as of 2022/07/18, the date when this document is written.
