from datetime import datetime, timedelta

import factory
from app.db.models import Meeting


class MeetingFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Meeting

    id = factory.Sequence(lambda n: n + 1)
    title = factory.Faker("sentence", nb_words=3)
    start_date = factory.LazyFunction(lambda: datetime.now())
    duration = factory.Faker("random_int", min=15, max=120)
    location = factory.Faker("address")
    notes = factory.Faker("text")
    num_reschedules = factory.Faker("random_int", min=0, max=5)
    reminder_sent = factory.Faker("boolean")
    completed = factory.Faker("boolean")

    @classmethod
    def as_dict(cls, **kwargs):
        """Generate a dict with ISO 8601 datetime strings."""
        obj = cls.build(**kwargs)
        return {
            key: (value.isoformat() if isinstance(value, datetime) else value)
            for key, value in obj.__dict__.items()
            if not key.startswith("_")
        }
