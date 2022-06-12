from checkpointing.decorator.func_call.processor.base import FuncCallIdentifierBase
from checkpointing.decorator.func_call.context import Context
from checkpointing.decorator.func_call._typing import ContextId

class FuncCallHashIdentifier(FuncCallIdentifierBase):
    def identify(self, context: Context) -> ContextId:
        """
        Identifies the context by producing a hash value, taking the following variables into account:

        
        - parameter values
        """





