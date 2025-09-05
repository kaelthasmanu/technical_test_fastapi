from fastapi import APIRouter

from app.api.v2.endpoints.auth import router as auth_router

routers = APIRouter()
router_list = [auth_router]

for router in router_list:
    existing = getattr(router, "tags", None) or []
    router.tags = existing + ["v2"]
    routers.include_router(router)
