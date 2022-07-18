from joblib import Memory

memory = Memory(".joblib", verbose=0)

a = 1

@memory.cache
def foo():
    return a


if __name__ == "__main__":
    print(foo())
