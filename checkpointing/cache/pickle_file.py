from checkpointing.cache.base import CacheBase
from checkpointing._typing import ReturnValue
from checkpointing import defaults
from checkpointing.exceptions import CheckpointNotExist
import pathlib
import os
import pickle


class PickleFileCache(CacheBase):
    """Cache the result as pickle files saved on the disk."""

    def __init__(self, directory: os.PathLike = None, pickle_protocol: int = pickle.DEFAULT_PROTOCOL) -> None:
        """
        Args:
            directory: the directory where the files will be saved. The directory will be created if it does not exist.
            pickle_protocol: the protocol used when pickling files
        """

        self.__directory = pathlib.Path(directory if directory is not None else defaults["cache.filesystem.directory"])
        self.__directory.mkdir(parents=True, exist_ok=True)

        self.__pickle_protocol = pickle_protocol

    def get_file_path(self, context_id: str) -> pathlib.Path:
        """
        Args:
            context_id: the file name without the file extension

        Returns:
            The full file path used in this cache that corresponds to the context id
        """

        filename = f"{context_id}.pickle"
        return self.__directory.joinpath(filename)

    def save(self, context_id: str, result: ReturnValue) -> None:
        """
        Save the result with the given context id.

        Args:
            context_id: identifier of the function call context, must be a valid file name without the file extension
            result: return value of the function call
        """

        with open(self.get_file_path(context_id), mode="wb") as file:
            pickle.dump(result, file, protocol=self.__pickle_protocol)

    def retrieve(self, context_id: str) -> ReturnValue:
        """
        Retrieve the function return value with the given context id.
        If there is no cached results for the context_id, throws a checkpointing.exceptions.CheckpointNotExist

        Args:
            context_id: identifier of the function call context, must be a valid file name without the file extension

        Returns:
            The return value of the function that corresponds to this context id
        """

        path = self.get_file_path(context_id)
        if not path.exists():
            raise CheckpointNotExist

        with open(path, mode="rb") as file:
            return pickle.load(file)
