import concurrent.futures  # Tätä tarvitaan toivottavasti tulevaisuudessa. (Haha, tulevaisuudessa... Hauska vitsi)
import threading
from typing import Any, List, Union

class KLThreadException(Exception):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__(self.message)

class StoppableThread:
    """
        Thread Handler for handling python-threads more easily.
        
        Every thread function should have a stop-argument as it's last argument for stop-lambda.
    """
    def __init__(self, target, thread_id: str = None, daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None):
        self.stopThread = False
        self.currently_running = False
        
        t_args: List[Any] = list(thread_args)
        t_args.append(lambda : self.stopThread)
        self.thread = threading.Thread(target=target, name=thread_id, daemon=daemon, args=t_args)
        
        if run_f != None: self.thread.run = run_f
        if startThread: self.Start()

    def Stop(self):
        self.stopThread = True

    def GetRunning(self) -> bool:
        if self.currently_running and not self.thread.is_alive():
            self.currently_running = False
        return self.currently_running
    
    def GetFinished(self) -> bool:
        return not self.GetRunning()

    def Start(self):
        if not self.currently_running:
            self.currently_running = True
            self.thread.start()
        
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
            
    
    def Start(self):
        if not self.currentlyRunning:
            self.currentlyRunning = True
            self.thread.start()
            
class ReturnThread:
    def __init__(self, target, startThread: bool = False, *thread_args: Any) -> None:
        self.currentlyRunning = False
        self.started = False
        
        self.executor = concurrent.futures.ThreadPoolExecutor()
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
            raise KLThreadException("Thread has to be started before fetching results!")
        
    def Dispose(self):
        self.thread.cancel()
        self.executor.shutdown()
        del self