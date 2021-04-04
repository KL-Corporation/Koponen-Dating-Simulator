import time
from typing import Callable

class PerformanceTimer():
    def __init__(self, identifier: str = None) -> None:
        self.startTime = -1
        self.stopTime = -1
        self.identifier = identifier

    def Start(self) -> None:
        self.startTime = time.perf_counter_ns()

    def Stop(self) -> None:
        self.stopTime = time.perf_counter_ns()
        if self.startTime == -1:
            raise RuntimeError("Timer needs to be started before stopping!")

    def PrintResult(self):
        if self.startTime == -1 or self.stopTime == -1:
            raise RuntimeError("Timer needs to be started and stopped before getting the result!")

        txt = "Execution "
        if self.identifier != None:
            txt += f"\"{self.identifier}\""
        txt += f"took {self.stopTime - self.startTime} nanoseconds."
        print(txt)

def timeit(func: Callable):
    """Decorator that prints the execution time."""
    def wrapper(*args, **kwargs):
        start = time.perf_counter_ns()
        output = func(*args, **kwargs)
        stop = time.perf_counter_ns()
        print(f"Execution of function \"{func.__name__}\" took {stop - start} nanoseconds.")
        return output
    return wrapper