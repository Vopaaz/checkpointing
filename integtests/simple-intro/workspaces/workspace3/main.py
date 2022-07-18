from checkpointing import checkpoint


@checkpoint()
def calc(a, b):
    print(f"calc is running for {a}, {b}")
    return a - b # Change from add to minus

if __name__ == "__main__":
    result = calc(1, 2) # Even though (1, 2) has been called, but the code has changed
    print(f"result: {result}") # So the result is new, -1
