from checkpointing import checkpoint

X = 0 # Global variable is renamed


@checkpoint()
def foo(t: int) -> int: # Argument is renamed and type annotation is added
    print("Running")
    result = t + X
    return result # However, the code logic does not change


if __name__ == "__main__":
    print(foo(1))
