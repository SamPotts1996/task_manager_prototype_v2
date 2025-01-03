import logging
import time
import threading
import psutil

logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self, max_memory_percent=80.0, max_cpu_percent=90.0, interval=5.0):
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent
        self.interval = interval
        self._stop_event = threading.Event()
        self.thread = None
        self.running = False

    def start(self):
        logger.debug("[ResourceManager] Starting resource monitor.")
        self.running = True
        self.thread = threading.Thread(target=self._monitor, daemon=True)
        self.thread.start()

    def stop(self):
        logger.info("[ResourceManager] Stopping resource monitor.")
        self.running = False
        if self.thread:
            self._stop_event.set()
            self.thread.join()

    def _monitor(self):
        while not self._stop_event.is_set():
            usage = self.get_resource_status()
            logger.debug(f"[ResourceManager] Updated usage: {usage}")
            # If usage too high, you might do something or skip tasks
            time.sleep(self.interval)

    def get_resource_status(self):
        return {
            "memory_available": psutil.virtual_memory().available,
            "memory_percent": psutil.virtual_memory().percent,
            "cpu_percent": psutil.cpu_percent(),
            "gpu_available": False  # You can add GPU logic if needed
        }
