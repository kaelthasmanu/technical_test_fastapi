from contextlib import AbstractContextManager
from typing import Callable, List, Optional

from sqlalchemy.orm import Session

from app.repository.base_repository import BaseRepository
from app.model.task import Task as TaskModel


class TaskRepository(BaseRepository):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        super().__init__(session_factory, TaskModel)

    def list_by_user(self, user_id: int) -> List[TaskModel]:
        with self.session_factory() as session:
            return session.query(self.model).filter(self.model.id_usuario == user_id).all()

    def get_by_id_and_user(self, task_id: int, user_id: int) -> Optional[TaskModel]:
        with self.session_factory() as session:
            return (
                session.query(self.model)
                .filter(self.model.id == task_id, self.model.id_usuario == user_id)
                .first()
            )

    def update_by_id_and_user(self, task_id: int, user_id: int, values: dict) -> Optional[TaskModel]:
        with self.session_factory() as session:
            updated = (
                session.query(self.model)
                .filter(self.model.id == task_id, self.model.id_usuario == user_id)
                .update(values)
            )
            session.commit()
            if updated:
                return self.get_by_id_and_user(task_id, user_id)
            return None

    def delete_by_id_and_user(self, task_id: int, user_id: int) -> bool:
        with self.session_factory() as session:
            obj = (
                session.query(self.model)
                .filter(self.model.id == task_id, self.model.id_usuario == user_id)
                .first()
            )
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True
