from checkpointing import checkpoint

X = 0


@checkpoint()
def foo(t):
    print("Running")
    z = t + X
    return z


if __name__ == "__main__":
    print(foo(1))
