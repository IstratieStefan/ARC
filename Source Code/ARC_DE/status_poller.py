import threading
import time
import subprocess

class StatusPoller:
    def __init__(self, poll_func, interval=2.0, initial=None):
        self.poll_func = poll_func
        self.interval = interval
        self.value = initial
        self.running = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._worker, daemon=True)

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False
        self.thread.join()

    def get(self):
        with self.lock:
            return self.value

    def _worker(self):
        while self.running:
            val = self.poll_func()
            with self.lock:
                self.value = val
            time.sleep(self.interval)



