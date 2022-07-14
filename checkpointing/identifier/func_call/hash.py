from checkpointing.identifier.func_call.base import FuncCallIdentifierBase
from checkpointing.identifier.func_call.context import FuncCallContext
from checkpointing._typing import ContextId
from checkpointing.config import defaults
from checkpointing.refactor.funcdef import FunctionDefinitionUnifier
from checkpointing.exceptions import GlobalStatementError, NonlocalStatementError
from typing import Dict
import textwrap
import copy

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

        if algorithm is None:
            algorithm = defaults["hash.algorithm"]

        if pickle_protocol is None:
            pickle_protocol = defaults["hash.pickle_protocol"]

        if unify_code is None:
            unify_code = defaults["identifier.func_call.unify_code"]

        self.algorithm = algorithm
        self.pickle_protocol = pickle_protocol
        self.unify_code = unify_code

    def identify(self, context: FuncCallContext) -> ContextId:
        """
        Identifies the context by producing a hash value.

        Returns:
            the function call context identifier
        """

        unifier = FunctionDefinitionUnifier(context.code)
        self.__check_unsupported_statements(unifier, context.code)

        if self.unify_code:
            return self.__identify_with_unification(context, unifier)
        else:
            return self.__identify_without_unification(context)

    def __check_unsupported_statements(self, unifier: FunctionDefinitionUnifier, original_code: str):
        error_text = lambda stmt_type: textwrap.dedent(
        f"""
        '{stmt_type}' statement detected in the code. This indicates that you are changing a {stmt_type} variable in the function, which is not a use case with checkpointing.
        Your code:
        {original_code}
        """
        )
        if unifier.has_global_statement:
            raise GlobalStatementError(error_text("global"))

        if unifier.has_nonlocal_statement:
            raise NonlocalStatementError(error_text("nonlocal"))

    def __identify_with_unification(self, context: FuncCallContext, unifier: FunctionDefinitionUnifier) -> ContextId:

        arguments = copy.copy(context.arguments)
        for old_name, new_name in unifier.args_renaming.items():
            arguments[new_name] = arguments.pop(old_name)

        return self.__identify_general(
            arguments,
            unifier.unified_ast_dump,
            context.module,
        )

    def __identify_without_unification(self, context: FuncCallContext) -> ContextId:
        return self.__identify_general(
            context.arguments,
            context.code,
            context.module,
        )

    def __identify_general(self, arguments: Dict, *others: str) -> ContextId:
        param_name_values = []
        for k, v in sorted(arguments.items()):
            param_name_values.append(k)
            param_name_values.append(v)

        return hash_anything(
            *param_name_values,
            *others,
            algorithm=self.algorithm,
            pickle_protocol=self.pickle_protocol,
        )