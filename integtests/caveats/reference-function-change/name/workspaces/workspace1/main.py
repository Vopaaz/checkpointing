from checkpointing import checkpoint


def qux(x):
    return x


@checkpoint()
def foo(x):
    print("Running")
    return qux(x)


if __name__ == "__main__":
    print(foo(0))
