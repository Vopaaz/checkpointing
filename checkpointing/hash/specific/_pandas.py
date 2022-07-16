import pandas as pd
from typing import Union
from checkpointing.hash.specific._numpy import hash_numpy_array
from checkpointing.hash._typing import Hash


def hash_pandas_object(obj: Union[pd.DataFrame, pd.Series]) -> bytes:
    np_arr = pd.util.hash_pandas_object(obj).values
    return hash_numpy_array(np_arr)
