from checkpointing.decorator.func_call.processor.base import FuncCallIdentifierBase
from checkpointing.decorator.func_call.context import Context
from checkpointing.decorator.func_call._typing import ContextId

class FuncCallHashIdentifier(FuncCallIdentifierBase):
    def identify(self, context: Context) -> ContextId:
        """
        Identifies the context by producing a hash value, taking the following variables into account:
        - function name
        - parameter values
        - function code

        # TODO: This is a temp solution, use advanced AST-based methods in the future
        # to eliminate the effect of naming of local variables or parameters.
        """
        
        pass





