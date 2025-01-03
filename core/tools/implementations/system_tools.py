import os
import platform
import psutil
from ..base_tool import BaseTool

class SystemInfo(BaseTool):
    def __init__(self):
        super().__init__(
            name="system_info",
            description="Get system information"
        )

    def execute(self) -> dict:
        return {
            'os': platform.system(),
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent
        }

class ProcessManager(BaseTool):
    def __init__(self):
        super().__init__(
            name="process_manager",
            description="Manage system processes"
        )

    def execute(self, action: str = "list", pid: Optional[int] = None) -> dict:
        if action == "list":
            return {
                'processes': [{
                    'pid': p.pid,
                    'name': p.name(),
                    'status': p.status()
                } for p in psutil.process_iter(['pid', 'name', 'status'])]
            }
        elif action == "kill" and pid:
            try:
                psutil.Process(pid).terminate()
                return {'status': 'success', 'message': f'Process {pid} terminated'}
            except:
                return {'status': 'error', 'message': f'Failed to terminate process {pid}'}