This page introduces the cases where you would expect the function to be re-executed,
but it's actually skipped by checkpointing and the vice versa.
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


## Changing reference function

checkpointing only watches the code change of the decorated function itself.
Any function invoked within it is only identified by reference,
meaning that the change of code logic cannot be captured.

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

The other side of this same problem is that,
renaming a reference function will the cause the decorated function to re-execute.

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
    Running
    0
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    def qux(x):
        return x

    @checkpoint()
    def foo(x):
        return qux(x)

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    Running
    0
    ```

Although `qux` and `bar` are doing the same thing, `foo` is re-executed.


We suggest to decouple your code logic,
such that the checkpointed function only invoke other functions that are known to be "static",
e.g. those from an external library.
Instead of invoking another custom function whose logic or name is likely to change in the future,
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


## Changing object method

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

The other side of this same problem is that,
renaming a method of the object will the cause the decorated function to re-execute.


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
        print("Running")
        bar.baz()
        return bar

    if __name__ == "__main__":
        bar = Bar()
        result = foo(bar)
        print(result.x)
    ```

    ```text title="Output"
    Running
    1
    ```

=== "2nd run"

    ```python title="script.py"
    from checkpointing import checkpoint

    class Bar:
        def __init__(self) -> None:
            self.x = 0

        def qux(self):
            self.x += 1

    @checkpoint()
    def foo(bar):
        print("Running")
        bar.qux()
        return bar

    if __name__ == "__main__":
        bar = Bar()
        result = foo(bar)
        print(result.x)
    ```

    ```text title="Output"
    Running
    1
    ```

Although `bar.baz()` and `bar.qux()` are doing the same thing,
`foo` is re-executed.

We suggest to only use objects whose methods are known to be "static",
e.g. those from an external library.



## Randomness

If the input parameter of a function is the result of a non-deterministic procedure,
user should properly set the random seed or equivalent fields to make sure that the parameters passed to the checkpointed function are exactly the same.

Although this is not a deflect of this package, it might cause problems in many common use cases in data science field if not paying attention.


=== "1st run"

    ```python title="script.py"
    from sklearn.linear_model import LogisticRegression
    from checkpointing import checkpoint


    def build_model():
        X = [[0], [1], [2], [3]]
        y = [0, 0, 1, 1]
        model = LogisticRegression(solver="saga") # saga makes the model random
        return model.fit(X, y)


    @checkpoint()
    def predict(model):
        print("Running")
        X = [[0], [1], [2], [3]]
        return model.predict(X).tolist()


    if __name__ == "__main__":
        model = build_model()
        prediction = predict(model)
        print(prediction)
    ```

    ```text title="Output"
    Running
    [0, 0, 1, 1]
    ```

=== "2nd run"

    ```python title="script.py"
    from sklearn.linear_model import LogisticRegression
    from checkpointing import checkpoint


    def build_model():
        X = [[0], [1], [2], [3]]
        y = [0, 0, 1, 1]
        model = LogisticRegression(solver="saga") # saga makes the model random
        return model.fit(X, y)


    @checkpoint()
    def predict(model):
        print("Running")
        X = [[0], [1], [2], [3]]
        return model.predict(X).tolist()


    if __name__ == "__main__":
        model = build_model()
        prediction = predict(model)
        print(prediction)
    ```

    ```text title="Output"
    Running
    [0, 0, 1, 1]
    ```

There is no difference between the two executed scripts,
however, the randomness in the `LogisticRegression` model causes its internal state to be different after the two estimations.
Therefore, in the 2nd run, the checkpoint cannot tell that this `model` is the same one as last time, so `predict` is re-executed.

The solution is to add a `random_state` parameter to the estimator,
so that its internal state will be reproducible as long as the training data is the same.

??? example "Full code and output after adding `random_state`"

    === "1st run"

        ```python title="script.py"
        from sklearn.linear_model import LogisticRegression
        from checkpointing import checkpoint


        def build_model():
            X = [[0], [1], [2], [3]]
            y = [0, 0, 1, 1]
            model = LogisticRegression(solver="saga", random_state=42)
            return model.fit(X, y)


        @checkpoint()
        def predict(model):
            print("Running")
            X = [[0], [1], [2], [3]]
            return model.predict(X).tolist()


        if __name__ == "__main__":
            model = build_model()
            prediction = predict(model)
            print(prediction)
        ```

        ```text title="Output"
        Running
        [0, 0, 1, 1]
        ```

    === "2nd run"

        ```python title="script.py"
        from sklearn.linear_model import LogisticRegression
        from checkpointing import checkpoint


        def build_model():
            X = [[0], [1], [2], [3]]
            y = [0, 0, 1, 1]
            model = LogisticRegression(solver="saga", random_state=42)
            return model.fit(X, y)


        @checkpoint()
        def predict(model):
            print("Running")
            X = [[0], [1], [2], [3]]
            return model.predict(X).tolist()


        if __name__ == "__main__":
            model = build_model()
            prediction = predict(model)
            print(prediction)
        ```

        ```text title="Output"
        [0, 0, 1, 1]
        ```

Alternatively, you can also checkpoint the function that builds the model.
The return values in the subsequent runs are guaranteed to be the same as the 1st run.


## Code changes

Although checkpointing is able to ignore many irrelevant modifications, such as renaming local variables,
in many cases it would still think some code change is significant enough such that the return value would change.



=== "1st run"

    ```python title="script.py"
    from checkpointing import checkpoint

    @checkpoint()
    def foo(x):
        print("Running")
        y = x + 1
        return y

    if __name__ == "__main__":
        print(foo(0))
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
        return x + 1

    if __name__ == "__main__":
        print(foo(0))
    ```

    ```text title="Output"
    Running
    1
    ```

Even though it's easy for a human to tell that the two executions of `foo` should give the same result,
checkpointing hasn't been able to do so yet.

