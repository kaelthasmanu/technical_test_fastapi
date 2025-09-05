from fastapi import APIRouter, HTTPException, status

from app.services.auth_service import AuthService
from app.schema.auth_schema import SignInResponse, SignIn
from app.core.container import Container
from fastapi import Depends


router = APIRouter()


def get_auth_service() -> AuthService:
    return Container.auth_service()

@router.post("/login", response_model=SignInResponse)
def login(request: SignIn, auth_service: AuthService = Depends(get_auth_service)):
    token = auth_service.authenticate_user(request)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return SignInResponse(access_token=token)

# Puedes agregar aquí más endpoints relacionados con autenticación si lo necesitas
