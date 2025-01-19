from app.db.models import Attendee
from app.db.repositories import AttendeeRepository
from app.schemas import AttendeeCreate, AttendeeUpdate
from app.services.base_service import BaseService


class AttendeeService(BaseService[Attendee, AttendeeCreate, AttendeeUpdate]):
    def __init__(self, repo: AttendeeRepository, redis_client=None):
        super().__init__(repo, model_name="Attendee", redis_client=redis_client)
