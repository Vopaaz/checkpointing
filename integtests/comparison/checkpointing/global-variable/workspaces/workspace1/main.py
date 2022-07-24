from checkpointing import checkpoint

a = 2 # The global variable has changed

@checkpoint()
def foo():
    return a


if __name__ == "__main__":
    print(foo()) # Thus the function will rerun and return 2
