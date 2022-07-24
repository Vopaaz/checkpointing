from checkpointing import checkpoint

N = 0


@checkpoint()
def foo():
    print("Running")
    b = N + 1
    return b


if __name__ == "__main__":
    print(foo())
