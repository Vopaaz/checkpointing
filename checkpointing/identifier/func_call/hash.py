from checkpointing.identifier.func_call.base import FuncCallIdentifierBase
from checkpointing.identifier.func_call.context import FuncCallContext
from checkpointing._typing import ContextId
from checkpointing.config import defaults
from checkpointing.refactor.unify.funcdef import FunctionDefinitionUnifier
from typing import Dict

from checkpointing.hash import hash_anything


class AutoHashIdentifier(FuncCallIdentifierBase):
    def __init__(self, algorithm: str = None, pickle_protocol: int = None, unify_code: bool = None) -> None:
        """
        Args:
            algorithm: the hash algorithm to use. If None, use the global default `hash.algorithm`.
            pickle_protocol: the pickle protocol to use. If None, use the global default `hash.pickle_protocol`
            unify_code: whether or not to enable code unification, which eliminates the effect of fundamental changes
                        in the code, such as formatting, adding type notations, and renaming local variables, etc.
                        If None, use the global default `identifier.func_call.unify_code`
        """
        self.algorithm = algorithm
        self.pickle_protocol = pickle_protocol

        if unify_code is None:
            unify_code = defaults["identifier.func_call.unify_code"]

        self.unify_code = unify_code

    def identify(self, context: FuncCallContext) -> ContextId:
        """
        Identifies the context by producing a hash value.

        Returns:
            the function call context identifier
        """

        if self.unify_code:
            self.__identify_with_unification(context)
        else:
            self.__identify_without_unification(context)

    def __identify_with_unification(self, context: FuncCallContext) -> ContextId:
        transformer = FunctionDefinitionUnifier()
        ast = transformer.get_unified_ast_dump(context.code)

        arguments = context.arguments
        for old_name, new_name in transformer.args_renaming.items():
            arguments[new_name] = arguments.pop(old_name)

        return self.__identify_general(arguments, ast)

    def __identify_without_unification(self, context: FuncCallContext) -> ContextId:
        return self.__identify_general(
            context.arguments,
            context.code,
        )

    def __identify_general(self, arguments: Dict, code: str) -> ContextId:
        param_name_values = []
        for k, v in arguments.items():
            param_name_values.append(k)
            param_name_values.append(v)

        return hash_anything(
            *param_name_values,
            code,
            algorithm=self.algorithm,
            pickle_protocol=self.pickle_protocol,
        )
