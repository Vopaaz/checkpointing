from checkpointing import checkpoint


@checkpoint()
def foo():
    # Adding comments will NOT cause the function to rerun
    print(f"Running")


if __name__ == "__main__":
    foo()
