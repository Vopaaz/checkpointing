from checkpointing import checkpoint


@checkpoint()
def foo(x):
    print("Running")
    y = x + 1
    return y


if __name__ == "__main__":
    print(foo(0))
