from joblib import Memory

memory = Memory(".joblib", verbose=0)


@memory.cache
def foo():
    print(f"Running")


if __name__ == "__main__":
    foo()
