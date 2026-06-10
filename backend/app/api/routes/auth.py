from fastapi import APIRouter, Depends

from app.middleware.auth_dependency import get_current_user
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
def register(
    payload: RegisterRequest, service: AuthService = Depends(AuthService)
) -> AuthResponse:
    result = service.register(payload.username, payload.email, payload.password)
    return AuthResponse(**result)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: LoginRequest, service: AuthService = Depends(AuthService)
) -> AuthResponse:
    result = service.login(payload.email, payload.password)
    return AuthResponse(**result)


@router.post("/logout", response_model=dict)
def logout(
    current_user: dict = Depends(get_current_user),
    service: AuthService = Depends(AuthService),
) -> dict:
    service.logout(current_user["id"])
    return {"message": "Successfully logged out"}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)) -> dict:
    return {"user": current_user}
