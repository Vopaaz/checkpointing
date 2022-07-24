from checkpointing import checkpoint

X = 1

@checkpoint()
def foo():
    print("Running")
    return X

if __name__ == "__main__":
    print(foo())
