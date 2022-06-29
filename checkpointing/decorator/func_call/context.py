import inspect
from typing import List, Dict, Tuple, Callable
from checkpointing._typing import ReturnValue


class Context:
    """
    Context of information for a function call.
    """

    def __init__(self, func: Callable[..., ReturnValue], args: Tuple, kwargs: Dict) -> None:
        """
        Args:
            args: the non-keywords arguments of the function call
            kwargs: the keyword arguments of the function call
            func: the function object that is being called
        """

        self.__func: Callable[..., ReturnValue] = func
        """Function called"""

        self.__args: Tuple = args
        """Arguments of the function call"""

        self.__kwargs: Dict = kwargs
        """Keyword arguments of the function call"""

        self.__signature = inspect.signature(self.__func)
        """Signature of the function"""

    @property
    def arguments(self) -> Dict:
        """
        Dictionary or OrderedDictionary (depending on the python version) of the function arguments and their actually applied parameter values in the function call.

        >>> def foo(a, b=1, c=None, d=4):
        ...     pass
        >>>
        >>> # Equivalent to the context computed for: foo(1, 2, c=3)
        >>> ctx = Context(foo, (1, 2), {"c": 3})
        >>>
        >>> dict(ctx.arguments)
        {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        """
        args = self.__signature.bind(*self.__args, **self.__kwargs)
        args.apply_defaults()
        return args.arguments

    @property
    def function_name(self) -> str:
        """
        The full name of the function.
        Specifically, the concatenation of a function's module and its [qualified name](https://docs.python.org/3/glossary.html#term-qualified-name).

        >>> def foo():
        ...     pass
        >>>
        >>> # Equivalent to the context computed for: foo()
        >>> ctx = Context(foo, (), {})
        >>>
        >>> # foo is defined in checkpointing/decorator/func_call/context.py
        >>> ctx.function_name
        'checkpointing.decorator.func_call.context.foo'
        """
        return ".".join([self.__func.__module__, self.__func.__qualname__])

    @property
    def function_code(self) -> str:
        r"""
        The source code of the function, including the function signature,
        formatted as-is, including any comments.

        >>> def foo(a, b):
        ...     c = a + b  # add a and b
        ...     return c
        >>>
        >>> # Equivalent to the context computed for: foo(1, 2)
        >>> ctx = Context(foo, (1, 2), {})
        >>>
        >>> ctx.function_code
        'def foo(a, b):\n    c = a + b  # add a and b\n    return c\n'
        """

        return inspect.getsource(self.__func)

    @property
    def local_variables(self) -> Tuple[str]:
        """
        The names of local variables and parameter names in the function.

        >>> def foo(a, b):
        ...     c = a + b
        ...     return c
        >>>
        >>> ctx = Context(foo, (1, 2), {})
        >>> ctx.local_variables
        ('a', 'b', 'c')

        Note that, if a variable was firstly global then assigned a local value, it's still included.

        >>> from collections import deque
        >>>
        >>> def bar():
        ...     a = deque() # The right hand side is actually not a local variable
        ...     deque = 1   # But it's converted to a local variable here
        >>>
        >>> ctx = Context(bar, (), {})
        >>> ctx.local_variables
        ('deque', 'a')
        """

        return self.__func.__code__.co_varnames
