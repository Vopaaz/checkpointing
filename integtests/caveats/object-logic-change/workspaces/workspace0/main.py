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
