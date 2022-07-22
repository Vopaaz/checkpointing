from cachier import cachier

@cachier()
def foo(x):
    return x


if __name__ == "__main__":
    print(foo(0))
