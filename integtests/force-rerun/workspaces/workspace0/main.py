from checkpointing import checkpoint

@checkpoint()
def foo(a):
    print("Running")

if __name__ == "__main__":
    foo(1)
