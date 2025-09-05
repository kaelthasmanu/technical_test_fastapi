from typing import Optional
from datetime import datetime

from sqlmodel import Field

from app.model.base_model import BaseModel


class Task(BaseModel, table=True):
    __tablename__ = "tasks"

    titulo: str
    descripcion: Optional[str] = None
    estado: str = Field(default="pendiente")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    id_usuario: int = Field(foreign_key="user.id")
