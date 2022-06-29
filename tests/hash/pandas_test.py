from checkpointing.hash import hash_anything
import pandas as pd


def test_hash_same_pandas_dataframe_gives_same_results():
    a = pd.DataFrame({"a": [1, 2, 3]})
    b = pd.DataFrame({"a": [1, 2, 3]})
    assert hash_anything(a) == hash_anything(b)

def test_hash_different_pandas_dataframe_gives_different_results():
    a = pd.DataFrame({"a": [1, 2, 3]})
    b = pd.DataFrame({"a": [1, 2, 4]})
    assert hash_anything(a) != hash_anything(b)

def test_hash_same_pandas_series_gives_same_results():
    a = pd.Series([1, 2, 3])
    b = pd.Series([1, 2, 3])
    assert hash_anything(a) == hash_anything(b)

def test_hash_different_pandas_series_gives_different_results():
    a = pd.Series([1, 2, 3])
    b = pd.Series([1, 2, 4])
    assert hash_anything(a) != hash_anything(b)
