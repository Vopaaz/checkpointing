from hashlib import algorithms_available

class CacheConfig:
    directory = ".checkpointing"
    """
    Directory used to store the cache.
    """

class HashConfig:
    algorithm = "md5"
    """
    Used hash algorithm.
    """
