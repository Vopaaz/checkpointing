from joblib import Memory

memory = Memory(".joblib", verbose=0)

a = 2 # The global variable has changed

@memory.cache
def foo():
    return a


if __name__ == "__main__":
    print(foo()) # But the execution is skipped and will return 1
