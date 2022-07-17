from joblib import Memory

memory = Memory(".joblib", verbose=0)


@memory.cache
def foo():
    # Adding comments will cause the function to rerun
    print(f"Running") 


if __name__ == "__main__":
    foo()
