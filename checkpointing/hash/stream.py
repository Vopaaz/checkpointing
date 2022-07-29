import hashlib
from checkpointing.config import defaults
from typing import Iterable
from io import RawIOBase


class HashStream(RawIOBase):
    """
    Binary input stream hasher. It implements a file-like interface, so that it can be used with
    pickle easily, without needing a copy of the bytes representation of an object and thus saving memory.
    """

    def __init__(self, algorithm: str = None) -> None:
        """
        Args:
            algorithm: the hash algorithm. Must be supported by the hashlib.
                        If it's not specified, use the global default `hash.algorithm`.
        """

        if algorithm is None:
            algorithm = defaults["hash.algorithm"]

        self.__hash = hashlib.new(algorithm)

    def readable(self) -> bool:
        return False

    def seekable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def writelines(self, lines: Iterable[bytes]) -> None:
        for line in lines:
            self.write(line)

    def write(self, b: bytes) -> int:
        self.__hash.update(b)
        return len(b)

    def hexdigest(self) -> str:
        """
        Returns:
            The hexdigest of the all the bytes data written to this hash stream
        """

        return self.__hash.hexdigest()
