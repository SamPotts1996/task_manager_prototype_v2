import heapq
import threading

class TaskQueue:
    """
    A simple priority queue for tasks, thread-safe.
    """
    def __init__(self):
        self.queue = []
        self.lock = threading.Lock()

    def push(self, task: dict, priority: int = 1):
        with self.lock:
            heapq.heappush(self.queue, (priority, task))

    def pop(self):
        with self.lock:
            if not self.queue:
                return None
            priority, task = heapq.heappop(self.queue)
            return task
