from checkpointing import checkpoint

@checkpoint()
def foo(x):
    return x - 1 # Code logic is changed, so it gets rerun


if __name__ == "__main__":
    print(foo(0))
