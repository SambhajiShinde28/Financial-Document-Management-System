from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.role import Role
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    MAX_PASSWORD_BYTES = 72

    @staticmethod
    def register(db: Session, payload: RegisterRequest) -> TokenResponse:
        if len(payload.password.encode("utf-8")) > AuthService.MAX_PASSWORD_BYTES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is too long. Please keep it under 72 bytes.",
            )

        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists.",
            )

        user = User(
            full_name=payload.full_name,
            email=payload.email,
            password_hash=hash_password(payload.password),
        )

        is_first_user = db.query(User).count() == 0
        if is_first_user:
            admin_role = db.query(Role).filter(Role.name == "Admin").first()
            if admin_role:
                user.roles.append(admin_role)

        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token)

    @staticmethod
    def login(db: Session, payload: LoginRequest) -> TokenResponse:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
            )

        token = create_access_token(str(user.id))
        return TokenResponse(access_token=token)
