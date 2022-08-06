"""
**Persistent cache for Python functions.**

See the documentation for each submodule for detail.
"""


from checkpointing.exceptions import CheckpointNotExist
from checkpointing.config import defaults
from checkpointing.decorator import DecoratorCheckpoint, checkpoint
from checkpointing.identifier import FuncCallIdentifierBase, AutoFuncCallIdentifier
from checkpointing.cache import CacheBase, PickleFileCache
from checkpointing._typing import ContextId, ReturnValue

try:
    from IPython import InteractiveShell
    from checkpointing.ipython import CellCheckpoint

    def load_ipython_extension(ipy: InteractiveShell) -> None:
        ipy.register_magics(CellCheckpoint)

except ImportError:
    pass
