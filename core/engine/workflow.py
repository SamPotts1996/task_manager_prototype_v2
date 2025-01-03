from typing import Dict, Any, List
from queue import Queue
from threading import Lock
import uuid

class WorkflowStep:
    def __init__(self, name: str, action: str, inputs: Dict = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.action = action
        self.inputs = inputs or {}
        self.status = "pending"
        self.output = None
        self.next_steps: List[str] = []

class Workflow:
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.steps: Dict[str, WorkflowStep] = {}
        self.entry_points: List[str] = []
        self.status = "pending"

class WorkflowEngine:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.step_queue = Queue()
        self.lock = Lock()

    def create_workflow(self, name: str) -> Workflow:
        workflow = Workflow(name)
        self.workflows[workflow.id] = workflow
        return workflow

    def add_step(self, workflow_id: str, step: WorkflowStep) -> str:
        with self.lock:
            wf = self.workflows.get(workflow_id)
            if not wf:
                raise ValueError(f"Workflow {workflow_id} not found.")
            wf.steps[step.id] = step
            if not wf.entry_points:
                wf.entry_points.append(step.id)
            return step.id

    def connect_steps(self, workflow_id: str, from_step_id: str, to_step_id: str):
        with self.lock:
            wf = self.workflows.get(workflow_id)
            if not wf:
                raise ValueError(f"Workflow {workflow_id} not found.")
            from_step = wf.steps.get(from_step_id)
            to_step = wf.steps.get(to_step_id)
            if not from_step or not to_step:
                raise ValueError("Invalid step IDs.")
            from_step.next_steps.append(to_step_id)

    def execute_workflow(self, workflow_id: str) -> Dict:
        wf = self.workflows.get(workflow_id)
        if not wf:
            raise ValueError(f"Workflow {workflow_id} not found.")

        for step_id in wf.entry_points:
            self.step_queue.put((workflow_id, step_id))

        results = {}
        while not self.step_queue.empty():
            wf_id, step_id = self.step_queue.get()
            step = self.workflows[wf_id].steps[step_id]

            try:
                step.status = "running"
                step.output = self._execute_step(step)
                step.status = "completed"
                results[step_id] = step.output
                for nxt in step.next_steps:
                    self.step_queue.put((workflow_id, nxt))
            except Exception as e:
                step.status = "failed"
                break

        return results

    def _execute_step(self, step: WorkflowStep) -> Any:
        # Example only
        if step.action == "task_creation":
            return {"type": "task", "content": "Generated a new task."}
        elif step.action == "task_execution":
            return {"type": "result", "content": "Executed the task."}
        elif step.action == "evaluation":
            return {"type": "evaluation", "content": "Evaluation result."}
        else:
            raise ValueError(f"Unknown action: {step.action}")
