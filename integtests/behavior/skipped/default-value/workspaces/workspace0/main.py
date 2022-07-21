from checkpointing import checkpoint

@checkpoint()
def foo(a = 1):
    print("Running")
    return a


if __name__ == "__main__":
    print(foo())
