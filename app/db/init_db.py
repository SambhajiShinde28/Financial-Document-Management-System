from sqlalchemy.orm import Session

from app.models.role import Role


DEFAULT_ROLE_PERMISSIONS: dict[str, list[str]] = {
    "Admin": [
        "documents:create",
        "documents:read",
        "documents:delete",
        "documents:index",
        "roles:create",
        "users:assign-role",
        "users:view-roles",
        "users:view-permissions",
    ],
    "Financial Analyst": [
        "documents:create",
        "documents:read",
        "documents:index",
    ],
    "Auditor": [
        "documents:read",
        "users:view-roles",
        "users:view-permissions",
    ],
    "Client": [
        "documents:read",
    ],
}


def seed_roles(db: Session) -> None:
    for role_name, permissions in DEFAULT_ROLE_PERMISSIONS.items():
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if existing_role:
            continue
        db.add(Role(name=role_name, permissions=",".join(permissions)))
    db.commit()
