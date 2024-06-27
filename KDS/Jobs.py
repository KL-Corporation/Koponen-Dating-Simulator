from __future__ import annotations

from concurrent.futures import *
import os
from typing import Any, Callable, Generic, ParamSpec, Self, Sequence, TypeVar, Union
import KDS.Math
import KDS.Logging

_T = TypeVar("_T")
_P = ParamSpec("_P")

def init():
    global executor
    # threadCount = os.cpu_count()
    # workerCount = KDS.Math.Clamp(threadCount if threadCount != None else -1, 4, 16)
    workerCount = 4 # We really don't need more than 4, because if it goes on the same thread as the main thread, then it will be slower.
    executor = ThreadPoolExecutor(max_workers=workerCount, thread_name_prefix="Jobs")
    KDS.Logging.debug(f"Setting up {workerCount} worker threads for Jobs.")

def quit():
    executor.shutdown(wait=True, cancel_futures=True)

class JobHandle(Generic[_T]):
    def __init__(self, *, _future: Future[_T]) -> None:
        self._future = _future

    @property
    def IsComplete(self) -> bool:
        return self._future.done()

    def Complete(self) -> _T:
        """Ensures that the job has completed.

        Returns:
            Any: The job function's output.
        """
        return self._future.result()

    def AddErrorLogger(self) -> Self:
        self._future.add_done_callback(JobHandle._handle_error_callback)
        return self

    @staticmethod
    def _handle_error_callback(future: Future) -> None:
        exc: BaseException | None = future.exception()
        if exc is not None:
            KDS.Logging.AutoError(exc)

    @staticmethod
    def CompleteAll(jobs: Sequence[JobHandle]) -> None:
        """Ensures that all jobs have completed.

        Args:
            jobs (Sequence[JobHandle]): The jobs to complete.
        """
        wait((f._future for f in jobs), return_when=ALL_COMPLETED)

def Schedule(function: Callable[_P, _T], *args: _P.args, **kwargs: _P.kwargs) -> JobHandle[_T]:
    """Schedule the job for execution on a worker thread.

    Args:
        function (Callable): The job and data to schedule.
        dependsOn (JobHandle, optional): Dependencies are used to ensure that a job executes on workerthreads after the dependency has completed execution. Making sure that two jobs reading or writing to same data do not run in parallel. Defaults to None.

    Returns:
        JobHandle: The handle identifying the scheduled job. Can be used as a dependency for a later job or ensure completion on the main thread.
    """
    return JobHandle(_future=executor.submit(function, *args, **kwargs))

#region OLD KDS.THREADING CODE
# import concurrent.futures  # Tätä tarvitaan toivottavasti tulevaisuudessa. (Haha, tulevaisuudessa... Hauska vitsi)
# import threading
# from typing import Any, List, Union
#
# class ThreadException(Exception):
#     def __init__(self, message) -> None:
#         self.message = message
#         super().__init__(self.message)
#
# class Thread:
#     def __init__(self, target, thread_id: str = None, daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None) -> None:
#         self.currentlyRunning = False
#
#         self.thread = threading.Thread(target=target, name=thread_id, daemon=daemon, args=thread_args)
#         if run_f != None: self.thread.run = run_f
#         if startThread: self.Start()
#
#     def GetRunning(self) -> bool:
#         if self.currentlyRunning and not self.thread.is_alive():
#             self.currentlyRunning = False
#         return self.currentlyRunning
#
#     def GetFinished(self) -> bool:
#         return not self.GetRunning()
#
#     def Start(self):
#         if not self.currentlyRunning:
#             self.currentlyRunning = True
#             self.thread.start()
#
#     def WaitForExit(self, timeout: float = None):
#         if self.thread.is_alive():
#             self.thread.join(timeout)
#
# class StoppableThread(Thread):
#     """
#         Thread Handler for handling python-threads more easily.
#
#         Every thread function should have a stop-argument as it's last argument for stop-lambda.
#     """
#     def __init__(self, target, thread_id: str = None, daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None):
#         self.stopThread = False
#
#         t_args: List[Any] = list(thread_args)
#         t_args.append(lambda : self.stopThread)
#         super().__init__(target, thread_id, daemon, startThread, *t_args, run_f=run_f)
#
#     def Stop(self):
#         self.stopThread = True
#         self.WaitForExit()
#
# class ReturnableThread:
#     def __init__(self, target, thread_id: str = "", startThread: bool = False, *thread_args: Any) -> None:
#         self.currentlyRunning = False
#         self.started = False
#
#         self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix=thread_id)
#         self.thread = None
#         self.target = target
#         self.args = thread_args
#
#         if startThread: self.Start()
#
#     def Start(self):
#         if not self.currentlyRunning:
#             self.currentlyRunning = True
#             self.started = True
#             self.thread = self.executor.submit(self.target, *self.args)
#
#     def GetRunning(self) -> bool:
#         if self.currentlyRunning and self.thread.done():
#             self.currentlyRunning = False
#         return self.currentlyRunning
#
#     def GetResult(self, timeout: float = None) -> Any:
#         if self.started:
#             return self.thread.result(timeout)
#         else:
#             raise ThreadException("Thread has to be started before fetching results!")
#
#     def Dispose(self):
#         self.thread.cancel()
#         self.executor.shutdown()
#         del self
#endregion
