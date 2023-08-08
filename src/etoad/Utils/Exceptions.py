class WorkflowError(Exception):
    """Base class for specific exceptions related to workflow management."""

    def __init__(self, *args):
        super().__init__(*args)


class SkipExecution(WorkflowError):
    """Exception to be raised when a certain operation is to be skipped."""

    def __init__(self, *args):
        super().__init__(*args)


class StopExecution(WorkflowError):
    """Exception to be raised when a certain measurement should be cancelled."""

    def __init__(self, *args):
        super().__init__(*args)


def log_exceptions(func):
    """
    Decorator to log any exceptions before raising them.
    Can be applied to any instance method of a class that has a self.logger attribute.
    """
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            if hasattr(self, "logger"):
                self.logger.error(f"Exception raised in function {self.__class__.__name__}.{func.__name__}: {e}")
            raise e

    return wrapper
