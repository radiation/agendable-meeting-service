from datetime import datetime
import uuid

import factory

from app.db.models.meeting import Meeting
from app.db.models.recurrence import Recurrence
from app.db.models.task import Task
from app.db.models.user import User
from app.schemas.meeting_schemas import MeetingCreate
from app.schemas.recurrence_schemas import RecurrenceCreate
from app.schemas.task_schemas import TaskCreate
from app.schemas.user_schemas import UserCreate


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def as_dict(cls, **kwargs):
        """Convert factory object to dict & serialize UUID / datetime fields"""
        obj = cls.build(**kwargs)
        return {
            key: (
                str(value)
                if isinstance(value, uuid.UUID)
                else value.isoformat()
                if isinstance(value, datetime)
                else value
            )
            for key, value in obj.__dict__.items()
            if not key.startswith("_")
        }

    class Meta:
        abstract = True


class MeetingFactory(BaseFactory):
    class Meta:
        model = Meeting

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker("sentence", nb_words=3)
    start_date = factory.LazyFunction(staticmethod(datetime.now))
    duration = factory.Faker("random_int", min=15, max=120)
    location = factory.Faker("address")
    notes = factory.Faker("text")
    num_reschedules = factory.Faker("random_int", min=0, max=5)
    reminder_sent = factory.Faker("boolean")
    completed = factory.Faker("boolean")


class MeetingCreateFactory(factory.Factory):
    class Meta:
        model = MeetingCreate

    title = factory.Faker("sentence", nb_words=3)
    start_date = factory.LazyFunction(staticmethod(datetime.now))
    duration = factory.Faker("random_int", min=15, max=120)


class RecurrenceFactory(BaseFactory):
    class Meta:
        model = Recurrence

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker("sentence", nb_words=3)
    rrule = factory.Iterator(
        [
            "FREQ=DAILY;INTERVAL=1;BYHOUR=14;BYMINUTE=30",
            "FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=10;BYMINUTE=00",
            "FREQ=MONTHLY;BYMONTHDAY=15;BYHOUR=17;BYMINUTE=00",
            "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25;BYHOUR=00;BYMINUTE=00",
        ]
    )
    created_at = factory.Faker("date_time")


class RecurrenceCreateFactory(factory.Factory):
    class Meta:
        model = RecurrenceCreate

    title = factory.Faker("sentence", nb_words=3)
    rrule = factory.Iterator(
        [
            "FREQ=DAILY;INTERVAL=1;BYHOUR=14;BYMINUTE=30",
            "FREQ=WEEKLY;BYDAY=MO,WE,FR;BYHOUR=10;BYMINUTE=00",
            "FREQ=MONTHLY;BYMONTHDAY=15;BYHOUR=17;BYMINUTE=00",
            "FREQ=YEARLY;BYMONTH=12;BYMONTHDAY=25;BYHOUR=00;BYMINUTE=00",
        ]
    )


class TaskFactory(BaseFactory):
    class Meta:
        model = Task

    id = factory.Sequence(lambda n: n + 1)
    assignee_id = factory.Faker("random_int", min=1, max=10)
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("text")
    due_date = factory.Faker("date_time")
    completed = factory.Faker("boolean")
    completed_date = factory.Faker("date_time")
    created_at = factory.Faker("date_time")


class TaskCreateFactory(factory.Factory):
    class Meta:
        model = TaskCreate

    assignee_id = factory.Faker("random_int", min=1, max=10)
    title = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("text")
    due_date = factory.Faker("date_time")


class UserFactory(BaseFactory):
    class Meta:
        model = User

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class UserCreateFactory(factory.Factory):
    class Meta:
        model = UserCreate

    id = factory.LazyFunction(uuid.uuid4)
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
