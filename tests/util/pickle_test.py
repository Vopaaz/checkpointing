from checkpointing.util import _pickle
from testutils import rmdir_after, tmpdir, mkdir_before
from pytest import raises

def test_too_high_protocol_raises_error():
    with raises(RuntimeError):
        _pickle.get_pickle_module(6)

def test_dump_load_file(mkdir_before, rmdir_after):
    with open(tmpdir.joinpath("pickle.data"), "wb") as f:
        _pickle.dump(1, f)

    with open(tmpdir.joinpath("pickle.data"), "rb") as f:
        n = _pickle.load(f)

    assert n == 1
