from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import require_permission
from app.db.session import get_db
from app.schemas.role import RoleCreateRequest, RoleResponse
from app.services.role_service import RoleService


router = APIRouter(tags=["Roles"])


@router.post("/roles/create", response_model=RoleResponse)
def create_role(
    payload: RoleCreateRequest,
    db: Session = Depends(get_db),
    _=Depends(require_permission("roles:create")),
):
    role = RoleService.create_role(db, payload)
    return RoleResponse(id=role.id, name=role.name, permissions=role.permission_list())
