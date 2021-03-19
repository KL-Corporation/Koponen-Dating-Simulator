import concurrent.futures  # Tätä tarvitaan toivottavasti tulevaisuudessa. (Haha, tulevaisuudessa... Hauska vitsi)
import threading
from typing import Any, List, Union

class ThreadException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class Thread:
    def __init__(self, target, thread_id: str = None, daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None) -> None:
        self.currentlyRunning = False

        self.thread = threading.Thread(target=target, name=thread_id, daemon=daemon, args=thread_args)
        if run_f != None: self.thread.run = run_f
        if startThread: self.Start()

    def GetRunning(self) -> bool:
        if self.currentlyRunning and not self.thread.is_alive():
            self.currentlyRunning = False
        return self.currentlyRunning

    def GetFinished(self) -> bool:
        return not self.GetRunning()

    def Start(self):
        if not self.currentlyRunning:
            self.currentlyRunning = True
            self.thread.start()

    def WaitForExit(self, timeout: float = None):
        if self.thread.is_alive():
            self.thread.join(timeout)

class StoppableThread(Thread):
    """
        Thread Handler for handling python-threads more easily.

        Every thread function should have a stop-argument as it's last argument for stop-lambda.
    """
    def __init__(self, target, thread_id: str = None, daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None):
        self.stopThread = False

        t_args: List[Any] = list(thread_args)
        t_args.append(lambda : self.stopThread)
        super().__init__(target, thread_id, daemon, startThread, *t_args, run_f=run_f)

    def Stop(self):
        self.stopThread = True
        self.WaitForExit()

class ReturnableThread:
    def __init__(self, target, thread_id: str = "", startThread: bool = False, *thread_args: Any) -> None:
        self.currentlyRunning = False
        self.started = False

        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=1, thread_name_prefix=thread_id)
        self.thread = None
        self.target = target
        self.args = thread_args

        if startThread: self.Start()

    def Start(self):
        if not self.currentlyRunning:
            self.currentlyRunning = True
            self.started = True
            self.thread = self.executor.submit(self.target, *self.args)

    def GetRunning(self) -> bool:
        if self.currentlyRunning and self.thread.done():
            self.currentlyRunning = False
        return self.currentlyRunning

    def GetResult(self, timeout: float = None) -> Any:
        if self.started:
            return self.thread.result(timeout)
        else:
            raise ThreadException("Thread has to be started before fetching results!")

    def Dispose(self):
        self.thread.cancel()
        self.executor.shutdown()
        del self