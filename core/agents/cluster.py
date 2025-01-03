from core.agents.base import BaseAgent
from core.agents.executor import ExecutorAgent
from core.agents.planner import PlannerAgent

# Also includes optional multi-agent cluster code
from typing import Dict, List, Optional
import threading
from queue import Queue, Empty
from core.engine.broker import MessageBroker
# We'll keep the cluster logic here if you want multi-agent setups

class AgentCluster:
    def __init__(self, name: str, broker: MessageBroker):
        self.name = name
        self.broker = broker
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue = Queue()
        self.result_queue = Queue()
        self._running = False
        self._workers: List[threading.Thread] = []

    def add_agent(self, agent_id: str, agent: BaseAgent):
        self.agents[agent_id] = agent
        self.broker.subscribe(f"agent.{agent_id}", self._handle_agent_message)

    def remove_agent(self, agent_id: str):
        if agent_id in self.agents:
            del self.agents[agent_id]

    def start(self, num_workers: int = 3):
        self._running = True
        for _ in range(num_workers):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self._workers.append(worker)

    def stop(self):
        self._running = False
        for worker in self._workers:
            worker.join()

    def _worker_loop(self):
        while self._running:
            try:
                task = self.task_queue.get(timeout=1)
                agent_id = self._select_agent(task)
                if agent_id and agent_id in self.agents:
                    result = self.agents[agent_id].process(task)
                    self.result_queue.put((task, result))
                self.task_queue.task_done()
            except Empty:
                continue

    def _select_agent(self, task: Dict) -> Optional[str]:
        # Implement agent selection logic
        return next(iter(self.agents)) if self.agents else None

    def _handle_agent_message(self, message: Dict):
        message_type = message.get('type')
        if message_type == 'task_complete':
            self.broker.publish('cluster.results', message)
        elif message_type == 'status_update':
            pass

class AgentPool:
    def __init__(self, broker: MessageBroker):
        self.broker = broker
        self.clusters: Dict[str, AgentCluster] = {}

    def create_cluster(self, name: str) -> AgentCluster:
        cluster = AgentCluster(name, self.broker)
        self.clusters[name] = cluster
        return cluster

    def remove_cluster(self, name: str):
        if name in self.clusters:
            self.clusters[name].stop()
            del self.clusters[name]

    def get_cluster(self, name: str) -> Optional[AgentCluster]:
        return self.clusters.get(name)

    def list_clusters(self) -> List[str]:
        return list(self.clusters.keys())


__all__ = ['BaseAgent', 'ExecutorAgent', 'PlannerAgent', 'AgentCluster', 'AgentPool']
