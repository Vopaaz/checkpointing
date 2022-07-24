from checkpointing import checkpoint


@checkpoint()
def foo(x):
    print("Running")
    return x + 1


if __name__ == "__main__":
    print(foo(0))
