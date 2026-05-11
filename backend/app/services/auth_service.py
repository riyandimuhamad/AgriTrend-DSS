from typing import Any

from fastapi import HTTPException

from app.core.supabase_client import get_supabase_client


class AuthService:
    def __init__(self) -> None:
        self.client = get_supabase_client()

    def register(self, email: str, password: str) -> dict[str, Any]:
        try:
            # Supabase Auth akan membuat user baru (dan bisa memicu email verification).
            response = self.client.auth.sign_up({"email": email, "password": password})
            session = response.session.model_dump() if response.session else {}
            return {
                "access_token": session.get("access_token"),
                "refresh_token": session.get("refresh_token"),
                "user": response.user.model_dump() if response.user else None,
                "message": "Register berhasil. Jika token kosong, cek email verifikasi Supabase.",
            }
        except Exception as exc:
            raise HTTPException(
                status_code=self._map_status(str(exc)),
                detail=self._clean_error(str(exc)),
            ) from exc

    def logout(self, access_token: str) -> dict[str, Any]:
        try:
            self.client.auth.sign_out(access_token)
            return {"message": "Logout berhasil."}
        except Exception as exc:
            raise HTTPException(
                status_code=self._map_status(str(exc)),
                detail=self._clean_error(str(exc)),
            ) from exc

    def login(self, email: str, password: str) -> dict[str, Any]:
        try:
            # Login with email/password via Supabase
            response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            if not response.session:
                raise HTTPException(
                    status_code=401,
                    detail="Login gagal. Cek email/password atau verifikasi email.",
                )
            session = response.session.model_dump()
            return {
                "access_token": session.get("access_token"),
                "refresh_token": session.get("refresh_token"),
                "user": response.user.model_dump() if response.user else None,
                "message": "Login berhasil.",
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
            # Validasi access token: jika valid, Supabase mengembalikan profil user.
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
        # Mapping error text Supabase ke HTTP status yang lebih bermakna.
        lowered = error_text.lower()
        if "rate limit" in lowered or "too many requests" in lowered:
            return 429
        if "email not confirmed" in lowered:
            return 403
        if "already" in lowered:
            return 409
        if "invalid" in lowered:
            return 401
        return 400

    @staticmethod
    def _clean_error(error_text: str) -> str:
        return error_text.strip() or "Supabase auth error"
