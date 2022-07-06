import inspect
from typing import List, Dict, Tuple, Callable
from checkpointing._typing import ReturnValue
from checkpointing.refactor.unify.funcdef import FunctionDefinitionUnifier


class FuncCallContext:
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
        >>> ctx = FuncCallContext(foo, (1, 2), {"c": 3})
        >>>
        >>> dict(ctx.arguments)
        {'a': 1, 'b': 2, 'c': 3, 'd': 4}

        The varargs and kwargs can also be captured:

        >>> def bar(*args, **kwargs):
        ...     pass
        >>>
        >>> ctx = FuncCallContext(bar, (1, 2), {"c": 3})
        >>>
        >>> dict(ctx.arguments)
        {'args': (1, 2), 'kwargs': {'c': 3}}
        """
        args = self.__signature.bind(*self.__args, **self.__kwargs)
        args.apply_defaults()
        return args.arguments

    @property
    def full_name(self) -> str:
        """
        The full name of the function.
        Specifically, the concatenation of a function's module and its [qualified name](https://docs.python.org/3/glossary.html#term-qualified-name).

        >>> def foo():
        ...     pass
        >>>
        >>> # Equivalent to the context computed for: foo()
        >>> ctx = FuncCallContext(foo, (), {})
        >>>
        >>> # foo is defined in checkpointing/identifier/func_call/context.py
        >>> ctx.full_name
        'checkpointing.identifier.func_call.context.foo'
        """
        return ".".join([self.module, self.qualified_name])

    @property
    def module(self) -> str:
        """
        Module where the function is defined.

        >>> def foo():
        ...     pass
        >>>
        >>> # Equivalent to the context computed for: foo()
        >>> ctx = FuncCallContext(foo, (), {})
        >>>
        >>> # foo is defined in checkpointing/identifier/func_call/context.py
        >>> ctx.module
        'checkpointing.identifier.func_call.context'
        """

        return self.__func.__module__

    @property
    def name(self) -> str:
        """
        Name of the function.

        >>> def foo():
        ...     pass
        >>>
        >>> # Equivalent to the context computed for: foo()
        >>> ctx = FuncCallContext(foo, (), {})
        >>> ctx.name
        'foo'
        """

        return self.__func.__name__

    
    @property
    def qualified_name(self) -> str:
        """
        [Qualified name](https://docs.python.org/3/glossary.html#term-qualified-name) of the function.

        >>> class Foo:
        ...     def bar(self):
        ...         pass
        >>>
        >>> f = Foo()
        >>>
        >>> # Equivalent to the context computed for: f.bar()
        >>> ctx = FuncCallContext(f.bar, (), {})
        >>> ctx.qualified_name
        'Foo.bar'
        """

        return self.__func.__qualname__

    @property
    def code(self) -> str:
        r"""
        The source code of the function, including the function signature,
        formatted as-is, including any comments.

        >>> def foo(a, b):
        ...     c = a + b  # add a and b
        ...     return c
        >>>
        >>> # Equivalent to the context computed for: foo(1, 2)
        >>> ctx = FuncCallContext(foo, (1, 2), {})
        >>>
        >>> ctx.code
        'def foo(a, b):\n    c = a + b  # add a and b\n    return c\n'
        """

        return inspect.getsource(self.__func)
