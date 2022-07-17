import pandas as pd
from cachier import cachier

@cachier()
def foo(x):
    print("Running")

if __name__ == "__main__":
    df = pd.DataFrame() # does not support pandas DataFrame as arguments
    try:
        foo(df)
    except TypeError as e:
        print("TypeError raised")
