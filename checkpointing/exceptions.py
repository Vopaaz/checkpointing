class CheckpointNotExist(Exception):
    pass

class CheckpointFailedError(RuntimeError):
    pass

class ExpensiveOverheadWarning(UserWarning):
    pass

class CheckpointFailedWarning(RuntimeWarning):
    pass

class RefactorFailedError(RuntimeError):
    pass

class GlobalStatementError(RuntimeError):
    pass

class NonlocalStatementError(RuntimeError):
    pass