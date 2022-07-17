from cachier import cachier

@cachier()
def foo(x):
    return x + 1


if __name__ == "__main__":
    print(foo(0))
