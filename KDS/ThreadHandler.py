from typing import Any, List
import threading
import concurrent.futures #Tätä tarvitaan toivottavasti tulevaisuudessa. (Haha, tulevaisuudessa... Hauska vitsi)

class KL_Thread: #KL_Thread toistaiseksi, koska en oo varma kuinka monta eri Thread-liittyvää keywordia on jo varattu.
    """
        Thread Handler for handling python-threads more easily.
        
        Every thread function should have a stop-argument as it's last argument for stop-lambda.
    """
    def __init__(self, target, thread_id: str, _daemon: bool = True, _startThread: bool = True, *thread_args: Any, run_f = None):
        if not thread_id: thread_id = None
        self.handled = False
        self.stopThread = False
        t_args: List[Any] = list(thread_args)
        t_args.append(lambda : self.stopThread)
        self.currently_running = _startThread
        self.thread = threading.Thread(target=target, name=thread_id, daemon=_daemon, args=t_args)
        if run_f: self.thread.run = run_f
        if _startThread: self.thread.start()

    def stop(self):
        self.stopThread = True

    def getRunning(self):
        if not self.thread.is_alive(): self.currently_running = False
        return self.currently_running
    
    def getFinished(self):
        if self.currently_running: return not self.getRunning()
        else: return False

    def start(self):
        self.thread.start()
        self.currently_running = True