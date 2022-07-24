from checkpointing import checkpoint

@checkpoint()
def foo():
    print(f"Running")


if __name__ == "__main__":
    foo()
