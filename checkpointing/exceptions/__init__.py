class CheckpointNotExist(Exception):
    pass

class CheckpointFailedError(RuntimeError):
    pass

class ExpensiveOverheadWarning(UserWarning):
    pass

class CheckpointFailedWarning(RuntimeWarning):
    pass
