from checkpointing import checkpoint


def bar(x):
    return x


@checkpoint()
def foo(x):
    print("Running")
    return bar(x)


if __name__ == "__main__":
    print(foo(0))
