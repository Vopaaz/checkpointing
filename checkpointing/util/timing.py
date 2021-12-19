import time


class Timer:
    def __init__(self) -> None:
        self.__start = None

    def start(self):
        self.__start = time.time()
        return self

    @property
    def time(self):
        if self.__start is None:
            raise RuntimeError("Timer.start() has never been called")

        return time.time() - self.__start
