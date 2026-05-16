from pydantic import BaseModel, EmailStr, Field

class UserSchema(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class RegisterRequest(UserSchema):
    username: str = Field(min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9]+$')

class LoginRequest(UserSchema):
    pass

class AuthResponse(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    user: dict | None = None
    message: str

class LogoutRequest(BaseModel):
    access_token: str