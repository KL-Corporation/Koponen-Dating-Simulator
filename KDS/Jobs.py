from __future__ import annotations

from concurrent.futures import *
import os
from typing import Any, Callable, Optional, Sequence, Union
import KDS.Math
import KDS.Logging

coreCount = os.cpu_count()
workerCount = KDS.Math.Clamp(coreCount if coreCount != None else -1, 4, 16)

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
    def CompleteAll(jobs: Sequence[JobHandle]) -> None:
        """Ensures that all jobs have completed.

        Complete needs to be called afterwards to get values or exceptions

        Args:
            jobs (Sequence[JobHandle]): The jobs to complete.
        """
        wait([f.future for f in jobs], return_when=ALL_COMPLETED)

def init():
    global executor
    executor = ThreadPoolExecutor(max_workers=workerCount, thread_name_prefix="Jobs") # Initializer to create the theards on start and not when required.
    KDS.Logging.debug(f"Setting up {workerCount} worker threads for Jobs.")

def quit():
    executor.shutdown(wait=True, cancel_futures=True)

def Schedule(function: Callable, *args: Any, **kwargs: Any) -> JobHandle:
    """Schedule the job for execution on a worker thread.

    Args:
        function (Callable): The job and data to schedule.
        dependsOn (JobHandle, optional): Dependencies are used to ensure that a job executes on workerthreads after the dependency has completed execution. Making sure that two jobs reading or writing to same data do not run in parallel. Defaults to None.

    Returns:
        JobHandle: The handle identifying the scheduled job. Can be used as a dependency for a later job or ensure completion on the main thread.
    """
    return JobHandle(executor.submit(function, *args, **kwargs))

class Process:
    executor: Optional[ProcessPoolExecutor] = None

    @staticmethod
    def init():
        Process.executor = ProcessPoolExecutor(max_workers=workerCount, )
        KDS.Logging.debug(f"Setting up {workerCount} worker threads for Process Jobs.")

    @staticmethod
    def quit():
        Process.executor.shutdown(wait=True, cancel_futures=True)

    @staticmethod
    def Schedule(function: Callable, *args: Any, **kwargs: Any) -> JobHandle:
        return JobHandle(Process.executor.submit(function, *args, **kwargs))

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