from checkpointing import checkpoint

X = 0


@checkpoint()
def foo():
    print("Running")
    z = X + 1
    return z


if __name__ == "__main__":
    print(foo())
