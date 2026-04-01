from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.role import Role
from app.models.user import User
from app.schemas.role import RoleCreateRequest


class RoleService:
    @staticmethod
    def create_role(db: Session, payload: RoleCreateRequest) -> Role:
        existing_role = db.query(Role).filter(Role.name == payload.name).first()
        if existing_role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role already exists.",
            )

        role = Role(name=payload.name, permissions=",".join(payload.permissions))
        db.add(role)
        db.commit()
        db.refresh(role)
        return role

    @staticmethod
    def assign_role(db: Session, user_id: int, role_name: str) -> User:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found.")

        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found.")

        if role not in user.roles:
            user.roles.append(role)
            db.commit()
            db.refresh(user)

        return user
