from checkpointing.hash import hash_anything
from checkpointing.exceptions import HashFailedWarning
import inspect
import warnings

def test_unhashable_objects_trigger_warning():
    with warnings.catch_warnings(record=True) as w:
        h1 = hash_anything(inspect.currentframe())
        h2 = hash_anything(inspect.currentframe())

        assert h1 != h2
        assert len(w) == 1
        assert issubclass(w[0].category, HashFailedWarning)

