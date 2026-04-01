from pydantic import BaseModel


class RoleCreateRequest(BaseModel):
    name: str
    permissions: list[str]


class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: list[str]
