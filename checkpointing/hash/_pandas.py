import pandas as pd
from typing import Union
from checkpointing.hash._numpy import hash_numpy_array
from checkpointing.hash._typing import Hash


def hash_pandas_object(hash_base: Hash, obj: Union[pd.DataFrame, pd.Series]) -> Hash:
    np_arr = pd.util.hash_pandas_object(obj).values
    return hash_numpy_array(hash_base, np_arr)
