from __future__ import annotations

from concurrent.futures import *
import os
from typing import Any, Callable, Sequence, Union
import KDS.Math
import KDS.Logging

def init():
    global executor
    coreCount = os.cpu_count()
    workerCount = KDS.Math.Clamp(coreCount if coreCount != None else -1, 2, 10)
    executor = ThreadPoolExecutor(max_workers=workerCount)
    KDS.Logging.debug(f"Setting up {workerCount} worker threads for Jobs.")

def quit():
    executor.shutdown(wait=False, cancel_futures=True)

class JobHandle:
    def __init__(self, future: Future) -> None:
        self.future = future

    def IsComplete(self) -> bool:
        return self.future.done()

    def Complete(self) -> Any:
        """Ensures that the job has completed.

        Returns:
            Any: The job function's output.
        """
        res = self.future.result()
        exc = self.future.exception()
        if exc != None:
            KDS.Logging.AutoError(str(exc))
        return res

    @staticmethod
    def CompleteAll(jobs: Sequence[JobHandle]):
        """Ensures that all jobs have completed.

        Args:
            jobs (Sequence[JobHandle]): The jobs to complete.
        """
        wait([f.future for f in jobs], return_when=ALL_COMPLETED)

def Schedule(function: Callable, *args: Any, **kwargs: Any) -> JobHandle:
    return JobHandle(executor.submit(function, *args, **kwargs))