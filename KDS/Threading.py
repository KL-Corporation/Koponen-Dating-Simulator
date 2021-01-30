import concurrent.futures  # Tätä tarvitaan toivottavasti tulevaisuudessa. (Haha, tulevaisuudessa... Hauska vitsi)
import threading
from typing import Any, List, Union


class StoppableThread:
    """
        Thread Handler for handling python-threads more easily.
        
        Every thread function should have a stop-argument as it's last argument for stop-lambda.
    """
    def __init__(self, target, thread_id: Union[str, None], daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None):
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
    def __init__(self, target, thread_id: Union[str, None], daemon: bool = True, startThread: bool = False, *thread_args: Any, run_f = None) -> None:
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