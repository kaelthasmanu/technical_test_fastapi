from typing import List, Optional

from pydantic import BaseModel

from app.schema.base_schema import FindBase, ModelBaseInfo, SearchOptions
from app.util.schema import AllOptional


from datetime import datetime

class BaseTask(BaseModel):
    id: Optional[int] = None
    titulo: str
    descripcion: Optional[str] = None
    estado: str
    fecha_creacion: datetime
    id_usuario: int

    class Config:
        from_attributes = True


class Task(ModelBaseInfo, BaseTask, metaclass=AllOptional): ...


class FindTasks(FindBase, BaseTask, metaclass=AllOptional):
    email__eq: str
    ...


class UpsertTask(BaseTask, metaclass=AllOptional): ...


class FindTaskResult(BaseModel):
    founds: Optional[List[Task]]
    search_options: Optional[SearchOptions]