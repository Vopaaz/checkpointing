from checkpointing import checkpoint


@checkpoint
def foo(a: int) -> int:
    print("Running")
    return a  # Add some comments


if __name__ == "__main__":
    print(foo(1))
