from app.db.models import User
from app.db.repositories import UserRepository
from app.schemas import UserCreate, UserUpdate
from app.services.base_service import BaseService


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, repo: UserRepository, redis_client=None):
        super().__init__(repo, model_name="User", redis_client=redis_client)
