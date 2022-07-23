from checkpointing import checkpoint

@checkpoint()
def foo(x):
    print("Running")
    return x

if __name__ == "__main__":
    print(foo(1))