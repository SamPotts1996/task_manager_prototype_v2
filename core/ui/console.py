import logging
import threading
from typing import Optional
from queue import Queue
from rich.console import Console
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ConsoleUI:
    def __init__(self, engine):
        self.engine = engine
        self.console = Console()
        self.input_queue = Queue()
        self.running = True
        self.layout = self._create_layout()
        self.logs = []

    def _create_layout(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="logs", size=10),
            Layout(name="input", size=3),
        )
        return layout

    def start(self):
        input_thread = threading.Thread(target=self._input_loop)
        input_thread.daemon = True
        input_thread.start()

        # Lower refresh to reduce DB calls
        with Live(self.layout, refresh_per_second=0.2) as live:
            while self.running:
                try:
                    while not self.input_queue.empty():
                        command = self.input_queue.get()
                        self._handle_command(command)

                    self._update_layout()
                    live.update(self.layout)
                    # Sleep 0.5s each loop => fewer "Getting pending tasks"
                    time.sleep(0.5)

                except KeyboardInterrupt:
                    self.running = False

    def _input_loop(self):
        while self.running:
            try:
                command = input("> ")
                self.input_queue.put(command)
            except (EOFError, KeyboardInterrupt):
                self.running = False

    def _handle_command(self, command: str):
        try:
            cmd_lower = command.lower().strip()

            if cmd_lower == "quit":
                self.running = False
            elif cmd_lower == "status":
                self._show_status()
                self.logs.append("[INFO] Displayed system status")
                logger.info("Displayed system status")
            elif cmd_lower == "resources":
                self._show_resources()
                self.logs.append("[INFO] Displayed resource usage")
                logger.info("Displayed resource usage")
            elif command.startswith("add "):
                task_text = command[4:].strip()
                self.engine.add_task({
                    "description": task_text,
                    "type": "task",
                    "priority": 1
                })
                self.logs.append(f"[INFO] Task added: {task_text}")
                logger.info(f"Task added: {task_text}")
            elif command.startswith("tool "):
                parts = command[5:].strip().split(" ", 1)
                if len(parts) == 2:
                    tool_name, args = parts
                    self.engine.add_task({
                        "type": "tool",
                        "tool_name": tool_name,
                        "tool_args": {"input": args},
                        "priority": 1
                    })
                    self.logs.append(f"[INFO] Tool task added: {tool_name} with args {args}")
                    logger.info(f"Tool task added: {tool_name} with args {args}")
            elif command.startswith("plan "):
                objective = command[5:].strip()
                tasks = self.engine.plan_objective(objective)
                self.logs.append(f"[INFO] Planned {len(tasks)} tasks for objective: {objective}")
                logger.info(f"Planned {len(tasks)} tasks for objective: {objective}")

            # Autonomy command
            elif cmd_lower.startswith("auto "):
                objective = command[5:].strip()
                self.engine.enable_autonomy(objective)
                self.logs.append(f"[INFO] Entered autonomous mode with objective: {objective}")
                logger.info(f"Entered autonomous mode with objective: {objective}")

            else:
                self.logs.append(f"[ERROR] Unknown command: {command}")
                logger.error(f"Unknown command: {command}")
                self.console.print("[red]Unknown command[/red]")
        except Exception as e:
            self.logs.append(f"[ERROR] Command failed: {str(e)}")
            logger.exception(f"Command failed: {command}")

    def _update_layout(self):
        self.layout["header"].update(
            Panel(f"SuperLocal Agent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Type 'help' for commands")
        )
        self.layout["main"].update(self._create_status_table())
        self.layout["logs"].update(self._create_logs_panel())
        self.layout["input"].update(
            Panel("> ", title="Input")
        )

    def _create_status_table(self) -> Table:
        table = Table(title="Current Tasks")
        table.add_column("ID")
        table.add_column("Type")
        table.add_column("Description")
        table.add_column("Status")

        tasks = self._refresh_tasks()
        for task in tasks:
            table.add_row(
                str(task.get("id", "?")),
                task.get("type", "task"),
                task.get("description", ""),
                task.get("status", "unknown")
            )
        return table

    def _create_logs_panel(self) -> Panel:
        log_content = "\n".join(self.logs[-10:])
        return Panel(log_content, title="Logs")

    def _refresh_tasks(self):
        return self.engine.get_tasks()

    def _show_resources(self):
        try:
            if hasattr(self.engine, 'resource_manager'):
                status = self.engine.resource_manager.get_resource_status()
                table = Table(title="Resource Status")
                table.add_column("Resource")
                table.add_column("Usage")
                table.add_row("CPU", f"{status['cpu_usage']}%")
                table.add_row("Memory", f"{status['memory_usage']}%")
                table.add_row("GPU", "Available" if status['gpu_available'] else "Not Available")
                self.console.print(table)
                self.logs.append("[INFO] Displayed resource status")
        except Exception as e:
            self.logs.append(f"[ERROR] Failed to display resources: {str(e)}")
            logger.exception(f"Failed to display resources: {e}")

    def _show_status(self):
        try:
            table = Table(title="System Status")
            table.add_column("Component")
            table.add_column("Status")
            table.add_row("Task Queue", str(len(self.engine.get_tasks())))
            table.add_row("Model", self.engine.config.get("model_path", "Not loaded"))
            self.console.print(table)
            self.logs.append("[INFO] Displayed system status")
        except Exception as e:
            self.logs.append(f"[ERROR] Failed to display system status: {str(e)}")
            logger.exception(f"Failed to display system status: {e}")
