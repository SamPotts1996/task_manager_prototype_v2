import logging
import sqlite3
import json
import os
import uuid
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class StateManager:
    def __init__(self, db_path: str = "agent_state.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            data TEXT,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        self.conn.commit()
        logger.debug("[StateManager] Database initialized.")

    def generate_id(self) -> str:
        return str(uuid.uuid4())

    def save_task(self, task: Dict):
        cursor = self.conn.cursor()
        task_id = task.get('id', self.generate_id())
        logger.info(f"[StateManager] Saving task {task_id}")
        cursor.execute(
            'INSERT INTO tasks (id, data, status) VALUES (?, ?, ?)',
            (task_id, json.dumps(task), task.get('status', 'pending'))
        )
        self.conn.commit()

    def get_task(self, task_id: str) -> Optional[Dict]:
        logger.debug(f"[StateManager] Fetching task {task_id}")
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM tasks WHERE id = ?', (task_id,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])
        return None

    def update_task(self, task_id: str, task: Dict):
        logger.info(f"[StateManager] Updating task {task_id} => {task.get('status')}")
        cursor = self.conn.cursor()
        cursor.execute(
            'UPDATE tasks SET data = ?, status = ? WHERE id = ?',
            (json.dumps(task), task.get('status', 'pending'), task_id)
        )
        self.conn.commit()

    def get_pending_tasks(self):
        logger.debug("[StateManager] Getting pending tasks")
        cursor = self.conn.cursor()
        cursor.execute('SELECT data FROM tasks WHERE status = ?', ('pending',))
        return [json.loads(row[0]) for row in cursor.fetchall()]

    def __del__(self):
        if hasattr(self, 'conn') and self.conn:
            logger.debug("[StateManager] Closing DB connection.")
            self.conn.close()
