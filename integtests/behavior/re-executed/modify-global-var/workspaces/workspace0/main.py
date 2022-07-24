from checkpointing import checkpoint

X = 0

@checkpoint()
def foo():
    print("Running")
    return X

if __name__ == "__main__":
    print(foo())
