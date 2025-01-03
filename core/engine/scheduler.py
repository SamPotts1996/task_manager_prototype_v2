import logging
import time
from .queue import TaskQueue
from ..memory.state import StateManager

logger = logging.getLogger(__name__)

class TaskScheduler:
    def __init__(self, queue: TaskQueue, state: StateManager):
        self.queue = queue
        self.state = state

    def schedule_task(self, task: dict):
        """
        Takes a task dict, ensures it has an ID, status, etc., saves it, and pushes to the queue.
        """
        if 'id' not in task:
            task['id'] = self.state.generate_id()
        if 'status' not in task:
            task['status'] = 'pending'
        if 'priority' not in task:
            task['priority'] = 1
        
        logger.info(f"[TaskScheduler] Scheduling task: {task}")
        self.queue.push(task, task['priority'])
        self.state.save_task(task)
        return task['id']

    def get_next_task(self):
        """
        Pops the highest priority task from the queue, updates to 'processing' in state, returns it.
        """
        next_task = self.queue.pop()
        if not next_task:
            return None
        # Mark it processing
        next_task['status'] = 'processing'
        self.state.update_task(next_task['id'], next_task)
        logger.debug(f"[TaskScheduler] Task now processing: {next_task['id']}")
        return next_task

    def complete_task(self, task_id: str, result: str):
        """
        Mark a task as complete in the DB.
        """
        logger.debug(f"[TaskScheduler] Marking task '{task_id}' complete.")
        task = self.state.get_task(task_id)
        if not task:
            return
        task['status'] = 'completed'
        task['result'] = result
        self.state.update_task(task_id, task)
