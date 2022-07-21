from checkpointing import checkpoint

@checkpoint()
def foo(a = 2):
    print("Running")
    return a


if __name__ == "__main__":
    print(foo(1))
