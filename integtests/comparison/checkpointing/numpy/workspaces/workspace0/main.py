import numpy as np
from checkpointing import checkpoint

@checkpoint()
def foo(x):
    return x

if __name__ == "__main__":
    df = np.arange(1) # supports pandas DataFrame as arguments
    try:
        foo(df)
    except:
        print("Error raised")
    else:
        print("No error") # there won't be error
