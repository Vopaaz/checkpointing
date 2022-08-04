from checkpointing.util import pickle
from testutils import rmdir_after, tmpdir, mkdir_before
from pytest import raises
from checkpointing.config import defaults

def test_too_high_protocol_raises_error():
    with raises(RuntimeError):
        pickle.get_pickle_module(6)

def test_dump_load_file(mkdir_before, rmdir_after):
    protocol = defaults["cache.pickle_protocol"]

    with open(tmpdir.joinpath("pickle.data"), "wb") as f:
        pickle.dump(1, f, protocol)

    with open(tmpdir.joinpath("pickle.data"), "rb") as f:
        n = pickle.load(f, protocol)

    assert n == 1
