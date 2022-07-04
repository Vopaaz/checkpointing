from typing import Union
from checkpointing.exceptions import RefactorFailedError
import ast


class FunctionDefTransformer(ast.NodeTransformer):
    def visit(
        self,
        node: Union[
            ast.FunctionDef,
            ast.AsyncFunctionDef,
        ],
    ) -> Union[ast.FunctionDef, ast.AsyncFunctionDef,]:

        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise RefactorFailedError(f"Fun")

        return super().visit(node)
