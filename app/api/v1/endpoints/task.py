from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.schema.task_schema import Task, UpsertTask
from dependency_injector.wiring import Provide, inject
from app.core.container import Container
from app.services.task_service import TaskService
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
@inject
def create_task(
    task: UpsertTask,
    user=Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    return task_service.create_task(task, user.id)

@router.get("/", response_model=List[Task])
@inject
def list_tasks(
    user=Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    return task_service.list_tasks(user.id)

@router.get("/{id}", response_model=Task)
@inject
def get_task(
    id: int,
    user=Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    task = task_service.get_task(id, user.id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{id}", response_model=Task)
@inject
def update_task(
    id: int,
    task: UpsertTask,
    user=Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    updated = task_service.update_task(id, task, user.id)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
    return updated

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
def delete_task(
    id: int,
    user=Depends(get_current_user),
    task_service: TaskService = Depends(Provide[Container.task_service]),
):
    deleted = task_service.delete_task(id, user.id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found or not authorized")
