from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.associations import user_roles


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(60), unique=True, nullable=False)
    permissions = Column(String(500), nullable=False, default="")

    users = relationship("User", secondary=user_roles, back_populates="roles")

    def permission_list(self) -> list[str]:
        if not self.permissions:
            return []
        return [item.strip() for item in self.permissions.split(",") if item.strip()]
