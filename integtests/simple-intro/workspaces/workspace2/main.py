from checkpointing import checkpoint


@checkpoint()
def calc(a, b):
    print(f"calc is running for {a}, {b}")
    return a + b

if __name__ == "__main__":
    result = calc(1, 3) # Parameters have changed, so the "calc is running for..." is printed
    print(f"result: {result}")
