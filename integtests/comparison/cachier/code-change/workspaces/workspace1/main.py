from cachier import cachier

@cachier()
def foo(x):
    return x - 1 # Code logic is changed, but still using the cached result


if __name__ == "__main__":
    print(foo(0))
