import logging
import sys
import time
import threading

from config import get_config
from core.models.llm import LlamaInterface
from core.models.embedding_minilm import MiniLMInterface
from core.memory.vector import VectorStorage
from core.memory.state import StateManager
from core.engine.scheduler import TaskScheduler
from core.engine.queue import TaskQueue
from core.engine.executor import TaskExecutor
from core.engine.broker import MessageBroker  # if you have it
from core.engine.resource_manager import ResourceManager
from core.agents.planner import PlannerAgent   # if you have it
from core.plugins.registry import PluginRegistry  # if you have it
from core.tools.marketplace import ToolMarketplace
from core.ui.console import ConsoleUI

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class SuperLocal:
    def __init__(self):
        # Load configuration
        self.config = get_config()

        # Initialize broker, resource manager, tools
        self.broker = MessageBroker()
        self.resource_manager = ResourceManager(
            max_memory_percent=self.config.get('max_memory_percent', 80.0),
            max_cpu_percent=self.config.get('max_cpu_percent', 90.0)
        )
        self.tool_marketplace = ToolMarketplace()

        # Initialize Llama for generation
        self.llm = LlamaInterface(
            model_path=self.config["model_path"],
            n_ctx=self.config["n_ctx"]
        )

        # Initialize MiniLM for embeddings
        self.embedder = MiniLMInterface(
            model_path=self.config["embedding_model_path"],
            n_ctx=512,
            n_threads=4,
            n_batch=128
        )

        # Initialize vector storage with embedding interface
        self.memory = VectorStorage(embedding_interface=self.embedder)

        # Initialize state, queue, scheduler, executor
        self.state = StateManager(self.config.get('state_db_path', 'agent_state.db'))
        self.queue = TaskQueue()
        self.scheduler = TaskScheduler(self.queue, self.state)
        self.executor = TaskExecutor(
            llm=self.llm,
            memory=self.memory,
            resource_manager=self.resource_manager,
            tool_marketplace=self.tool_marketplace,
            broker=self.broker
        )

        # If you have a Planner agent or plugin registry:
        self.planner = PlannerAgent(self.llm, self.memory)  # or pass embedder if needed
        self.plugins = PluginRegistry()

        # UI
        self.ui = ConsoleUI(self)

        # Start a background worker thread to auto-execute tasks
        self._running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def _worker_loop(self):
        """
        Continuously pull tasks from the queue and execute them.
        """
        while self._running:
            task = self.scheduler.get_next_task()
            if not task:
                time.sleep(1)  # No pending tasks, sleep briefly
                continue

            print(f"[WORKER] Picked up task '{task['description']}' (ID: {task['id']}).")
            result = self.execute_task(task)
            if result:
                print(f"[WORKER] Task '{task['description']}' completed with result:\n{result}\n")
                self.scheduler.complete_task(task['id'], result)
            else:
                print(f"[WORKER] Task '{task['description']}' had no result or failed.")
                task['status'] = 'failed'
                self.state.update_task(task['id'], task)

    def start(self):
        print("SuperLocal starting...")
        try:
            self.resource_manager.start()
            self.ui.start()
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        finally:
            self._cleanup()

    def _cleanup(self):
        try:
            self._running = False
            self.worker_thread.join()
            self.resource_manager.stop()
            self.broker.stop()
            # self.executor.stop() if needed
        except Exception as e:
            print(f"Error during cleanup: {e}")

    def add_task(self, task: dict):
        if not task.get('type'):
            task['type'] = 'task'
        return self.scheduler.schedule_task(task)

    def get_tasks(self):
        return self.state.get_pending_tasks()

    def execute_task(self, task: dict):
        return self.executor.execute_task(task)

    def plan_objective(self, objective: str):
        plan_result = self.planner.create_plan(objective)
        if plan_result:
            tasks = plan_result.get("tasks", [])
            for t in tasks:
                self.scheduler.schedule_task(t)
            return tasks
        return []

if __name__ == "__main__":
    agent = SuperLocal()
    agent.start()
