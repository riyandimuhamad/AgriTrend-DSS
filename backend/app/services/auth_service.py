from typing import Any

from fastapi import HTTPException

from app.core.supabase_client import get_supabase_client


class AuthService:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    def register(self, username: str, email: str, password: str) -> dict[str, Any]:
        try:
            response = self.client.auth.sign_up(
                {"username": username, "email": email, "password": password}
            )
            session = response.session.model_dump() if response.session else {}
            return {
                "access_token": session.get("access_token"),
                "refresh_token": session.get("refresh_token"),
                "user": response.user.model_dump() if response.user else None,
                "message": "Register Succesfully.",
            }
        except Exception as exc:
            raise HTTPException(
                status_code=self._map_status(str(exc)),
                detail=self._clean_error(str(exc)),
            ) from exc

    def login(self, email: str, password: str) -> dict[str, Any]:
        try:
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if not response.session:
                raise HTTPException(
                    status_code=401,
                    detail="Failed to Login..",
                )
            session = response.session.model_dump()
            return {
                "access_token": session.get("access_token"),
                "refresh_token": session.get("refresh_token"),
                "user": (
                    response.user.model_dump().get("username")
                    if response.user
                    else None
                ),
                "message": "Login Succesfully.",
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=self._map_status(str(exc)),
                detail=self._clean_error(str(exc)),
            ) from exc

    def get_user_from_token(self, access_token: str) -> dict[str, Any]:
        try:
            response = self.client.auth.get_user(access_token)
            if not response.user:
                raise HTTPException(status_code=401, detail="Token tidak valid.")
            return response.user.model_dump()
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=401, detail=self._clean_error(str(exc))
            ) from exc

    @staticmethod
    def _map_status(error_text: str) -> int:
        lowered = error_text.lower()
        if "rate limit" in lowered or "too many requests" in lowered:
            return 429
        if "email not confirmed" in lowered:
            return 403
        if "already registered" in lowered or "already exists" in lowered:
            return 409
        if "invalid login credentials" in lowered or "invalid password" in lowered:
            return 401
        return 400

    @staticmethod
    def _clean_error(error_text: str) -> str:
        return error_text.strip() or "Supabase auth error"
