from checkpointing.decorator.func_call.identifier.base import FuncCallIdentifierBase
from checkpointing.decorator.func_call.context import Context
from checkpointing._typing import ContextId

from checkpointing.hash import hash_anything


class FuncCallHashIdentifier(FuncCallIdentifierBase):
    def __init__(self, algorithm: str = None) -> None:
        """
        Args:
            algorithm: the hash algorithm to use. If None, use the default value
                        in the global configuration (`defaults["hash.algorithm"]`).
        """
        self.algorithm = algorithm

    def identify(self, context: Context) -> ContextId:
        """
        Identifies the context by producing a hash value, taking the following variables into account:
        - parameter names and their values
        - function code

        # TODO: This is a temp solution, use advanced AST-based methods in the future
        # to eliminate the effect of naming of local variables or parameters.
        """

        param_name_values = []
        for k, v in context.arguments.items():
            param_name_values.append(k)
            param_name_values.append(v)

        return hash_anything(*param_name_values, context.function_code, algorithm=self.algorithm)
