import pandas as pd
from typing import Union
from checkpointing.hash._numpy import hash_numpy_array


def hash_pd_obj(obj: Union[pd.DataFrame, pd.Series], algorithm: str = None) -> str:
    np_arr = pd.util.hash_pandas_object(obj)
    return hash_numpy_array(np_arr, algorithm=algorithm)
