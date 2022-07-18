import numpy as np
from cachier import cachier

@cachier()
def foo(x):
    return x

if __name__ == "__main__":
    df = np.arange(1) # does not support pandas DataFrame as arguments
    try:
        foo(df)
    except TypeError as e:
        print("TypeError raised") # and raises error
