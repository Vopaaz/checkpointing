from checkpointing import checkpoint


@checkpoint()
def bar(a):
    print("Running")
    return a


if __name__ == "__main__":
    print(bar(1))
