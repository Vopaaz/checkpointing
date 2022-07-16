from checkpointing.cache.pickle_file import PickleFileCache, CheckpointNotExist
import pickle
from tests.testutils import tmpdir, rmdir_before
from pytest import raises


def test_cache_creates_dir_automatically(rmdir_before):
    assert not tmpdir.exists()
    PickleFileCache(tmpdir)
    assert tmpdir.exists()


def test_cache_saves_result_to_pickle():

    value = [1, 2, 3]
    PickleFileCache(tmpdir).save("0", value)

    filepath = tmpdir.joinpath("0.pickle")
    assert filepath.exists()

    with open(filepath, "rb") as f:
        assert pickle.load(f) == value


def test_cache_retrieves_result():

    value = [1, 2, 3]
    cache = PickleFileCache(tmpdir)

    cache.save("1", value)
    assert cache.retrieve("1") == value


def test_cache_throws_CheckpointNotExist(rmdir_before):
    with raises(CheckpointNotExist):
        cache = PickleFileCache(tmpdir)
        cache.retrieve("0")
