from fastapi import APIRouter, Depends

from app.middleware.auth_dependency import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(payload: RegisterRequest, service: AuthService = Depends(AuthService)) -> AuthResponse:
    result = service.register(payload.email, payload.password)
    return AuthResponse(**result)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, service: AuthService = Depends(AuthService)) -> AuthResponse:
    result = service.login(payload.email, payload.password)
    return AuthResponse(**result)


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return {"user": current_user}

