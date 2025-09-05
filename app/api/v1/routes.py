from fastapi import APIRouter

#from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.task import router as task_router
# user endpoints are removed from v1

routers = APIRouter()
#router_list = [auth_router, task_router]
router_list = [task_router]

for router in router_list:
    # Ensure tags contains version info and keep any existing tags
    existing = getattr(router, "tags", None) or []
    router.tags = existing + ["v1"]
    routers.include_router(router)
