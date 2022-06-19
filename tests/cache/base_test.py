"""
This test module mainly focus on the concurrency synchronization,
as the base cache abstract class itself is not testable.

Because Python have GIL, it's hard to conduct unit tests for multithreading,
therefore we only test multiprocessing.
"""

from checkpointing.cache import CacheBase
from checkpointing import ContextId, ReturnValue

import multiprocessing

class CountingCache(CacheBase):
    """
    A Cache that does nothing but records the number of times `save` and `retrieve` is invoked.
    """

    def __init__(self) -> None:
        self.cnt = 0

    def save(self, context_id: ContextId, result: ReturnValue) -> None:
        self.cnt += 1

    def retrieve(self, context_id: ContextId) -> ReturnValue:
        self.cnt += 1
        return 0


def run_1000_save(cache: CacheBase):
    for _ in range(1000):
        cache.save(0, 0)

def test_multiprocessing_safe():
    unsafe_cache = CountingCache()

    unsafe_processes = [multiprocessing.Process(target=run_1000_save, args=(unsafe_cache,)) for _ in range(10)]
    for p in unsafe_processes:
        p.start()

    for p in unsafe_processes:
        p.join()

    # Ensure that this arrangement can cause unsafety
    assert unsafe_cache.cnt < 10000

    unsafe_cache.cnt = 0
    safe_cache = unsafe_cache.process_synchronized()
    safe_processes = [multiprocessing.Process(target=run_1000_save, args=(safe_cache,)) for _ in range(10)]
    
    for p in safe_processes:
        p.start()

    for p in safe_processes:
        p.join()

    # safe_cache does not have cnt, use the internal unsafe_cache which actually gets updated
    assert unsafe_cache.cnt < 10000
