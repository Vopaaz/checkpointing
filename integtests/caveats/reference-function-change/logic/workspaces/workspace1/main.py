from checkpointing import checkpoint


def bar(x):
    return x + 1


@checkpoint()
def foo(x):
    return bar(x)


if __name__ == "__main__":
    print(foo(0))
