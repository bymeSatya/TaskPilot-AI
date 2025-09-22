# services/__init__.py
# make services a package and expose task manager helpers
from .task_manager import load_tasks, save_tasks, add_task, get_task, update_task, delete_task
