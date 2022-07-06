from typing import Union, Dict, List, Any
from checkpointing.exceptions import RefactorFailedError
from checkpointing.refactor.util import local_variable_names_generator
import ast
from collections import deque, ChainMap
import textwrap
import copy


class FunctionDefinitionUnifier:
    def __init__(self) -> None:
        self.transformer = None
        super().__init__()

    @property
    def args_renaming(self):
        if self.transformer is None:
            raise RuntimeError(f"{self.__class__.__name__}.unify has not been invoked on any function definitions.")

        return self.transformer.root_function_args_renaming

    def get_unified_ast_dump(self, func_definition: str) -> str:
        """
        Returns:
            the dump string of the unified AST of the function definition.

        By unified, it means that
        - Type annotations are ignored
        - Function name is unified
        - Arguments, position-only arguments, and keyword-only arguments are renamed based on their 
          lexicographic order
        - Varargs and kwargs are renamed with a unique name
        - Default values of the arguments
        - Local variables are renamed based on their order of occurrence
        - AugAssign statements (a += 1) are replaced with normal assign statements (a = a + 1)

        Therefore, changing any aspect mentioned above will not change the returned AST dump.
        Also trivially, AST dump is not affected by the code formatting and comments.

        The criteria of the ignored/renamed/unified items above is:

        Given that the arguments are provided in a keyword-specified way, taking the renaming of 
        arguments into account, what changes will not cause the function return value to change.

        This is useful for judging whether two function definitions, given the same input,
        can produce the same output.
        """

        tree = ast.parse(textwrap.dedent(func_definition), mode="exec")
        if len(tree.body) > 1 or not isinstance(
            tree.body[0],
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.Lambda,
            ),
        ):
            raise RefactorFailedError(f"The given code is not a single function definition: {func_definition}")

        self.transformer = _FunctionDefinitionTransformer()
        unified_tree = self.transformer.visit(tree)

        return ast.dump(
            unified_tree,
            annotate_fields=False,
            include_attributes=False,
        )


class _FunctionDefinitionTransformer(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()

        self.local_variables = ChainMap()
        self.root_function_args_renaming = None
        self.names = local_variable_names_generator()

    def visit_AnyClosure(
        self,
        node: Union[
            ast.FunctionDef,
            ast.AsyncFunctionDef,
            ast.ClassDef,
        ],
        initial_map: Dict,
    ) -> Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,]:

        self.local_variables.maps.insert(0, initial_map)
        self.generic_visit(node)
        self.local_variables.maps.pop(0)

        return node

    @property
    def current_closure_local_variables(self):
        return self.local_variables.maps[0]

    def unify_arg(self, node: ast.arg, local_vars: Dict, new_name: str = None) -> None:
        old_name = node.arg

        if new_name is None:
            new_name = next(self.names)

        node.annotation = None
        node.arg = new_name
        local_vars[old_name] = new_name

    def unify_name(self, node: Any, local_vars: Dict) -> None:
        old_name = node.name
        new_name = next(self.names)

        node.name = new_name
        local_vars[old_name] = new_name

        return new_name

    def visit_AnyFunctionDef(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda],
    ) -> Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda]:

        new_function_name = self.unify_name(node, self.current_closure_local_variables)

        local_vars = {}
        args: List[ast.arg] = []

        for attrname in ["posonlyargs", "args", "kwonlyargs"]:
            if hasattr(node.args, attrname) and getattr(node.args, attrname) is not None:
                arglist = getattr(node.args, attrname)
                args.extend(arglist)
            setattr(node.args, attrname, [])

        for arg in sorted(args, key=lambda x: x.arg):
            self.unify_arg(arg, local_vars)

        for attrname in ["vararg", "kwarg"]:
            if hasattr(node.args, attrname) and getattr(node.args, attrname) is not None:
                self.unify_arg(
                    getattr(node.args, attrname),
                    local_vars,
                    f"{new_function_name}_{attrname}",
                )
            setattr(node.args, attrname, None)

        node.args.defaults = []
        node.args.kw_defaults = []
        node.returns = None

        if self.root_function_args_renaming is None:
            self.root_function_args_renaming = copy.deepcopy(local_vars)

        return self.visit_AnyClosure(node, local_vars)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        return self.visit_AnyFunctionDef(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        return self.visit_AnyFunctionDef(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        self.unify_name(node, self.current_closure_local_variables)
        return self.visit_AnyClosure(node, {})

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id in self.local_variables:
            return ast.Name(id=self.local_variables[node.id], ctx=node.ctx)

        elif isinstance(node.ctx, ast.Store):
            new_name = next(self.names)
            self.current_closure_local_variables[node.id] = new_name
            return ast.Name(id=new_name, ctx=node.ctx)

    def visit_Global(self, node: ast.Global) -> ast.Global:
        for name in node.names:
            self.current_closure_local_variables[name] = name
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.Nonlocal:
        return ast.Nonlocal(
            names=[self.local_variables[n] for n in node.names],
        )

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.Assign:
        assign = ast.Assign(
            targets=[node.target],
            value=node.value if hasattr(node, "value") else ast.Constant(value=None),
        )

        self.generic_visit(assign)
        return assign

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AugAssign:
        assign = ast.Assign(
            targets=[node.target],
            value=ast.BinOp(
                left=node.target,
                op=node.op,
                right=node.value,
            ),
        )

        self.generic_visit(assign)
        return assign

    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        self.visit_AnyFunctionDef(node)
