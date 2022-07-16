from typing import Union, Dict, List, Any
from checkpointing.exceptions import RefactorFailedError
from checkpointing.refactor.util import local_variable_names_generator, nonlocal_variable_names_generator
import ast
from collections import deque, ChainMap
import textwrap
import copy


class FunctionDefinitionUnifier:
    def __init__(self, func_definition: str) -> None:
        tree = ast.parse(textwrap.dedent(func_definition), mode="exec")
        if len(tree.body) > 1 or not isinstance(
            tree.body[0],
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            raise RefactorFailedError(f"The given code is not a single function definition: {func_definition}")

        self.transformer = _FunctionDefinitionTransformer()
        self.unified_tree = self.transformer.visit(tree)

    @property
    def args_renaming(self) -> Dict[str, str]:
        """
        Dictionary of the renaming of function arguments.

        >>> code = '''
        ...     def foo(a):
        ...         pass
        ...     '''
        >>>
        >>> u = FunctionDefinitionUnifier(code)
        >>> u.args_renaming
        {'a': '__checkpointing_local_var_1__'}
        """

        return self.transformer.root_function_args_renaming

    @property
    def nonlocal_variables_renaming(self) -> Dict[str, str]:
        """
        Dictionary of the renaming of nonlocal variables referenced by the function.

        >>> code = '''
        ...     def foo():
        ...         a = b + 1 # b is some global variable defined elsewhere
        ...     '''
        >>>
        >>> u = FunctionDefinitionUnifier(code)
        >>> u.nonlocal_variables_renaming
        {'b': '__checkpointing_nonlocal_var_0__'}
        """

        return self.transformer.nonlocal_variables

    @property
    def has_global_statement(self) -> bool:
        return self.transformer.has_global_statement

    @property
    def has_nonlocal_statement(self) -> bool:
        return self.transformer.has_nonlocal_statement

    @property
    def unified_ast_dump(self) -> str:
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
        - Global variables are renamed based on their order of occurrence
        - AugAssign statements (a += 1) are replaced with normal assign statements (a = a + 1)

        Therefore, changing any aspect mentioned above will not change the returned AST dump.
        Also trivially, AST dump is not affected by the code formatting and comments.

        The criteria of the ignored/renamed/unified items above is:

        Given that the arguments are provided in a keyword-specified way, taking the renaming of
        arguments into account, what changes will not cause the function return value to change.

        This is useful for judging whether two function definitions, given the same input,
        can produce the same output.
        """

        return ast.dump(
            self.unified_tree,
            annotate_fields=False,
            include_attributes=False,
        )


class _FunctionDefinitionTransformer(ast.NodeTransformer):
    def __init__(self) -> None:
        super().__init__()

        self.local_variables = ChainMap()
        self.root_function_args_renaming = None
        self.nonlocal_variables = {}

        self.has_global_statement = False
        self.has_nonlocal_statement = False

        self.local_names = local_variable_names_generator()
        self.nonlocal_names = nonlocal_variable_names_generator()

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
            new_name = next(self.local_names)

        node.annotation = None
        node.arg = new_name
        local_vars[old_name] = new_name

    def unify_name(self, node: Any, local_vars: Dict) -> None:
        old_name = node.name
        new_name = next(self.local_names)

        node.name = new_name
        local_vars[old_name] = new_name

        return new_name

    def visit_AnyFunctionDef(
        self,
        node: Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda],
    ) -> Union[ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda]:

        if isinstance(node, ast.Lambda):
            new_function_name = next(self.local_names)
        else:
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

        if node.id in self.local_variables:  # Local variables that are already renamed
            return ast.Name(id=self.local_variables[node.id], ctx=node.ctx)

        elif node.id in self.nonlocal_variables:  # Nonlocal variables that are already renamed
            return ast.Name(id=self.nonlocal_variables[node.id], ctx=node.ctx)

        elif isinstance(node.ctx, ast.Store):  # New local variable declaration
            new_name = next(self.local_names)
            self.current_closure_local_variables[node.id] = new_name
            return ast.Name(id=new_name, ctx=node.ctx)

        elif isinstance(node.ctx, ast.Load):  # New nonlocal variable reference
            new_name = next(self.nonlocal_names)
            self.nonlocal_variables[node.id] = new_name
            return ast.Name(id=new_name, ctx=node.ctx)

    def visit_Global(self, node: ast.Global) -> ast.Global:
        self.has_global_statement = True
        return node

    def visit_Nonlocal(self, node: ast.Nonlocal) -> ast.Nonlocal:
        self.has_nonlocal_statement = True
        return node

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.Assign:
        assign = ast.Assign(
            targets=[node.target],
            value=node.value if hasattr(node, "value") else ast.Constant(value=None),
        )

        self.generic_visit(assign)
        return assign

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AugAssign:
        new_target = _ContextStoreToLoadTransformer().visit(
            copy.copy(
                node.target,
            )
        )

        assign = ast.Assign(
            targets=[node.target],
            value=ast.BinOp(
                left=new_target,
                op=node.op,
                right=node.value,
            ),
        )

        self.generic_visit(assign)
        return assign

    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        return self.visit_AnyFunctionDef(node)


class _ContextStoreToLoadTransformer(ast.NodeTransformer):
    def visit_node_with_context(self, node: Union[ast.Attribute, ast.Subscript, ast.Starred, ast.Name, ast.List, ast.Tuple]):
        cp = copy.copy(node)
        cp.ctx = ast.Load()
        self.generic_visit(cp)
        return cp

    def visit_Attribute(self, node: ast.Attribute) -> Any:
        return self.visit_node_with_context(node)

    def visit_Subscript(self, node: ast.Subscript) -> Any:
        return self.visit_node_with_context(node)

    def visit_Starred(self, node: ast.Starred) -> Any:
        return self.visit_node_with_context(node)

    def visit_Name(self, node: ast.Name) -> Any:
        return self.visit_node_with_context(node)

    def visit_List(self, node: ast.List) -> Any:
        return self.visit_node_with_context(node)

    def visit_Tuple(self, node: ast.Tuple) -> Any:
        return self.visit_node_with_context(node)
