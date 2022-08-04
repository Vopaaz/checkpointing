from checkpointing.hash.stream import HashStream
from pytest import raises

def test_hash_stream_not_readable():
    with raises((OSError, NotImplementedError)):
        HashStream().read(1)

def test_hash_stream_not_seekable():
    with raises(OSError):
        HashStream().seek(1, 0)

def test_hash_stream_is_writable():
    HashStream().write(b"123")

def test_hash_stream_writelines_equivalence():
    h1 = HashStream()
    h2 = HashStream()

    h1.write(b"123")
    h2.writelines([b"1", b"2", b"3"])

    assert h1.hexdigest() == h2.hexdigest()
