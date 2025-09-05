from typing import List, Optional
from datetime import datetime

from app.schema.task_schema import Task, UpsertTask
from app.repository.task_repository import TaskRepository


class TaskService:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def create_task(self, task_data: UpsertTask, user_id: int) -> Task:
        payload = Task(
            titulo=task_data.titulo,
            descripcion=task_data.descripcion,
            estado=task_data.estado or "pendiente",
            fecha_creacion=datetime.utcnow(),
            id_usuario=user_id,
        )
        return self.task_repository.create(payload)

    def list_tasks(self, user_id: int) -> List[Task]:
        return self.task_repository.list_by_user(user_id)

    def get_task(self, task_id: int, user_id: int) -> Optional[Task]:
        return self.task_repository.get_by_id_and_user(task_id, user_id)

    def update_task(self, task_id: int, task_data: UpsertTask, user_id: int) -> Optional[Task]:
        values = {}
        if task_data.titulo is not None:
            values["titulo"] = task_data.titulo
        if task_data.descripcion is not None:
            values["descripcion"] = task_data.descripcion
        if task_data.estado is not None:
            values["estado"] = task_data.estado
        if not values:
            return self.get_task(task_id, user_id)
        return self.task_repository.update_by_id_and_user(task_id, user_id, values)

    def delete_task(self, task_id: int, user_id: int) -> bool:
        return self.task_repository.delete_by_id_and_user(task_id, user_id)
