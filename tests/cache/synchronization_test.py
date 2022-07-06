"""
This test module mainly focus on the concurrency synchronization,
as the base cache abstract class itself is not testable.

Because Python have GIL, it's hard to conduct unit tests for multithreading,
therefore we only test multiprocessing.
"""

from checkpointing.cache import CacheBase, PickleFileCache
from checkpointing import ContextId, ReturnValue, CheckpointNotExist

from tests.testutils import tmpdir, rmdir_before, rmdir_after

import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait
import multiprocessing


class IncrementalFileCache(PickleFileCache):
    """
    A Cache that does nothing but increments the number of times `save` is invoked.
    """

    def __init__(self, directory: os.PathLike = None) -> None:
        super().__init__(directory)

    def save(self, context_id: str, result: ReturnValue) -> None:
        res = self.retrieve(context_id)
        super().save(context_id, res + 1)

    def retrieve(self, context_id: str) -> ReturnValue:
        try:
            return super().retrieve(context_id)
        except CheckpointNotExist:
            return 0


def run_10_save(cache: CacheBase):
    for _ in range(10):
        cache.save("0", 0)


def test_multiprocessing_safe(rmdir_before, rmdir_after):

    unsafe_cache = IncrementalFileCache(tmpdir)
    lock = multiprocessing.Manager().Lock()
    safe_cache = unsafe_cache.synchronize_with(lock)

    futures = []
    with ProcessPoolExecutor() as e:
        for _ in range(5):
            f = e.submit(run_10_save, safe_cache)
            futures.append(f)

        wait(futures)

    assert safe_cache.retrieve("0") == 50

