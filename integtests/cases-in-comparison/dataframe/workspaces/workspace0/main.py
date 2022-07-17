import pandas as pd
from checkpointing import checkpoint

@checkpoint()
def foo(x):
    return x

if __name__ == "__main__":
    df = pd.DataFrame() # supports pandas DataFrame as arguments
    try:
        foo(df)
    except:
        print("Error raised")
    else:
        print("No error") # there won't be error
