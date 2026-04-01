from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserSummary(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AssignRoleRequest(BaseModel):
    user_id: int
    role_name: str
