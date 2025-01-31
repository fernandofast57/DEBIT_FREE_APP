
from enum import Enum
from typing import List
from app.models import User, Role
from app.database import db

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"

class ServizioRuoli:
    @staticmethod
    async def assign_role(user_id: int, role: UserRole):
        user = await db.session.query(User).get(user_id)
        if user:
            user.role = role.value
            await db.session.commit()
            
    @staticmethod
    async def has_permission(user_id: int, required_role: UserRole) -> bool:
        user = await db.session.query(User).get(user_id)
        if not user:
            return False
            
        roles_hierarchy = {
            UserRole.ADMIN.value: 3,
            UserRole.MANAGER.value: 2,
            UserRole.USER.value: 1
        }
        
        return roles_hierarchy.get(user.role, 0) >= roles_hierarchy.get(required_role.value, 0)
