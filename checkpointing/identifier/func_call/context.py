import inspect
from typing import List, Dict, Tuple, Callable, Any
from checkpointing._typing import ReturnValue
from types import FrameType
import copy


class FuncCallContext:
    """
    Context of information for a function call.
    """

    def __init__(self, func: Callable[..., ReturnValue], args: Tuple, kwargs: Dict, def_frame: FrameType = None,) -> None:
        """
        Args:
            func: the function object that is being called
            args: the non-keywords arguments of the function call
            kwargs: the keyword arguments of the function call
            def_frame: the frame where the function is defined
        """

        self.__func: Callable[..., ReturnValue] = func
        self.__args: Tuple = args
        self.__kwargs: Dict = kwargs
        self.__signature = inspect.signature(self.__func)

        if def_frame is not None:
            self.__locals = copy.copy(def_frame.f_locals)

        else:
            self.__locals = None

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

    def get_nonlocal_variable(self, varname: str) -> Any:
        r"""
        Try to get the nonlocal variable `varname` from the caller's frame.
        If it doesn't exist in neither `globals` and `locals`, return `None`.
        If the caller_frame is not provided, the result is always `None`.

        >>> import inspect
        >>>
        >>> a = 1
        >>> def foo():
        ...     pass
        >>>
        >>> ctx = FuncCallContext(foo, (), {}, inspect.currentframe())
        >>> ctx.get_nonlocal_variable("a")
        1
        >>> ctx.get_nonlocal_variable("b") is None
        True
        """

        if self.__locals is not None and varname in self.__locals:
            return self.__locals[varname]

        if self.__func.__globals__ is not None and varname in self.__func.__globals__:
            return self.__func.__globals__[varname]

        return None
