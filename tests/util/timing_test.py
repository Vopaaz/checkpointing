from checkpointing.util.timing import Timer, timed_run
from nose.tools import raises
from time import sleep


def test_timed_run_returns_correct_time():
    def foo():
        sleep(1)

    _, time = timed_run(foo)
    assert 0.8 <= time <= 1.2


def test_timed_run_returns_correct_result():
    def foo(a, b):
        return a + b, a - b

    res, _ = timed_run(foo, 1, b=2)
    assert res == (3, -1)


@raises(RuntimeError)
def test_timer_throws_error_when_start_is_not_called():
    t = Timer()
    return t.time
