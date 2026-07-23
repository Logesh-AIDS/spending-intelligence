from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    """Request body for registration."""
    email: EmailStr
    full_name: str
    password: str


class UserLogin(BaseModel):
    """Request body for login (though OAuth2PasswordRequestForm will be used)."""
    email: str
    password: str


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """Public user data (never send password or hash)."""
    id: int
    email: str
    full_name: str
    is_active: bool

    class Config:
        from_attributes = True  # allows Pydantic to read from SQLAlchemy models
