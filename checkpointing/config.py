import pickle

defaults = {
    "cache.filesystem.directory": ".checkpointing",
    "cache.pickle_protocol": pickle.DEFAULT_PROTOCOL,
    "hash.algorithm": "md5",
    "hash.pickle_protocol": pickle.DEFAULT_PROTOCOL,
    "checkpoint.on_error": "warn",
}
"""Package-wise global dict for default value configurations"""
