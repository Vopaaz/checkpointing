from checkpointing.util.timing import Timer
from nose.tools import raises
from time import sleep

def test_timer_returns_correct_time():
    t = Timer().start()
    sleep(0.1)
    assert 0.05 <= t.time <= 0.15


@raises(RuntimeError)
def test_timer_throws_error_when_start_is_not_called():
    t = Timer()
    return t.time
