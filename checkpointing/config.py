defaults = {
    "cache.filesystem.directory": ".checkpointing",
    "cache.pickle_protocol": 5,
    "hash.algorithm": "md5",
    "hash.pickle_protocol": 5,
    "checkpoint.on_error": "warn",
}
"""
Package-wise global dict for default value configurations

The pickle protocols are hardcoded as `5` in favor of [PEP 574](https://peps.python.org/pep-0574/),
which optimizes pickling large data objects. Using this will significantly reduce the memory overhead.
[pickle5](https://pypi.org/project/pickle5/) is used to provide as a backport for Python 3.7.
"""
