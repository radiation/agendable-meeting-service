from app.db.models.user import User
from app.db.repositories.user_repo import UserRepository
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, repo: UserRepository, redis_client=None):
        super().__init__(repo, redis_client=redis_client)
