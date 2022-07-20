from checkpointing import checkpoint

N = 0


@checkpoint()
def foo(a):
    print("Running")
    b = a + N
    return b


if __name__ == "__main__":
    print(foo(1))
