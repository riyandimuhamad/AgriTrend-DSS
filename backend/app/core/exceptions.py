from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


def error_payload(message: str, detail: Any = None) -> dict[str, Any]:
    return {"success": False, "message": message, "detail": detail}


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=error_payload("Request failed", exc.detail))

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(_: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content=error_payload("Validation error", exc.errors()))

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(status_code=500, content=error_payload("Internal server error", str(exc)))
