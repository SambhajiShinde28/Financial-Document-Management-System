from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import AssignRoleRequest
from app.services.role_service import RoleService


router = APIRouter(tags=["Users"])


@router.post("/users/assign-role")
def assign_role(
    payload: AssignRoleRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("users:assign-role")),
):
    user = RoleService.assign_role(db, payload.user_id, payload.role_name)
    return {"message": "Role assigned successfully.", "user_id": user.id}


@router.get("/users/{user_id}/roles")
def get_user_roles(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("users:view-roles")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"user_id": user.id, "roles": [role.name for role in user.roles]}


@router.get("/users/{user_id}/permissions")
def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_permission("users:view-permissions")),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    permissions = sorted(
        {
            permission
            for role in user.roles
            for permission in role.permission_list()
        }
    )
    return {"user_id": user.id, "permissions": permissions}
