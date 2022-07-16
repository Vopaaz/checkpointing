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
    def __init__(self, algorithm: str = None, pickle_protocol: int = None) -> None:
        """
        Args:
            algorithm: the hash algorithm to use. If None, use the global default `hash.algorithm`.
            pickle_protocol: the pickle protocol to use. If None, use the global default `hash.pickle_protocol`
        """

        if algorithm is None:
            algorithm = defaults["hash.algorithm"]

        if pickle_protocol is None:
            pickle_protocol = defaults["hash.pickle_protocol"]

        self.algorithm = algorithm
        self.pickle_protocol = pickle_protocol

    def identify(self, context: FuncCallContext) -> ContextId:
        """
        Identifies the context by producing a hash value.

        Returns:
            the function call context identifier
        """

        unifier = FunctionDefinitionUnifier(context.code)
        self.__check_unsupported_statements(unifier, context.code)

        return self.__identify_with_unifier(context, unifier)

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

    def __identify_with_unifier(self, context: FuncCallContext, unifier: FunctionDefinitionUnifier) -> ContextId:

        variables = copy.copy(context.arguments)

        for old_name, new_name in unifier.args_renaming.items():
            variables[new_name] = variables.pop(old_name)

        for old_name, new_name in unifier.nonlocal_variables_renaming.items():
            var = context.get_nonlocal_variable(old_name)
            variables[new_name] = var if var is not None else (old_name, "__checkpointing_no_nonlocal_reference__")

        return hash_anything(
            *sorted(variables.items()),
            unifier.unified_ast_dump,
            algorithm=self.algorithm,
            pickle_protocol=self.pickle_protocol,
        )
