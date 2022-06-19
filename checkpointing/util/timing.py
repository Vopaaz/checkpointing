"""
Utilities for timing a function.
"""

import time
from typing import Callable, Tuple, Dict, TypeVar


class Timer:
    """
    Keep track of the interval between two time points.
    """
    def __init__(self) -> None:
        self.__start = None

    def start(self):
        """
        Record the start time point.
        """
        self.__start = time.time()
        return self

    @property
    def time(self):
        """
        The total seconds between the latest `timer.start()` call and now.
        """
        if self.__start is None:
            raise RuntimeError("Timer.start() has never been called")

        return time.time() - self.__start

ReturnValue = TypeVar("ReturnValue")

def timed_run(func: Callable[..., ReturnValue], *args: Tuple, **kwargs: Dict) -> Tuple[ReturnValue, float]:
    """
    Run the function with the arguments, recording the run time.

    Returns:
        Tuple of two elements:
        - Return value of the function call
        - Time it takes to run the function
    """
    t = Timer().start()
    res = func(*args, **kwargs)
    return res, t.time
