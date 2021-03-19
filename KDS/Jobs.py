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

    def TryCancel(self) -> bool:
        return self.future.cancel()

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
    """Schedule the job for execution on a worker thread.

    Args:
        function (Callable): The job and data to schedule.
        dependsOn (JobHandle, optional): Dependencies are used to ensure that a job executes on workerthreads after the dependency has completed execution. Making sure that two jobs reading or writing to same data do not run in parallel. Defaults to None.

    Returns:
        JobHandle: The handle identifying the scheduled job. Can be used as a dependency for a later job or ensure completion on the main thread.
    """
    return JobHandle(executor.submit(function, *args, **kwargs))