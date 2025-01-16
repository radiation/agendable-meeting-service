from app.db.models import Attendee
from app.db.repositories.attendee_repo import AttendeeRepository
from app.schemas.attendee_schemas import AttendeeCreate, AttendeeUpdate
from app.services.base_service import BaseService


class AttendeeService(BaseService[Attendee, AttendeeCreate, AttendeeUpdate]):
    def __init__(self, repo: AttendeeRepository):
        super().__init__(repo, model_name="Attendee")
