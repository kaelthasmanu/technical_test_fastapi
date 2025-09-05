from dependency_injector import containers, providers

from app.core.config import configs
from app.core.database import Database
from app.repository.user_repository import UserRepository
from app.repository.task_repository import TaskRepository
from app.services import AuthService, UserService
from app.services.task_service import TaskService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "app.api.v1.endpoints.task",
            "app.api.v1.endpoints.user",
            "app.api.v2.endpoints.auth",
            "app.core.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)

    user_repository = providers.Factory(UserRepository, session_factory=db.provided.session)
    task_repository = providers.Factory(TaskRepository, session_factory=db.provided.session)

    auth_service = providers.Factory(AuthService, user_repository=user_repository)

    user_service = providers.Factory(UserService, user_repository=user_repository)
    task_service = providers.Factory(TaskService, task_repository=task_repository)
