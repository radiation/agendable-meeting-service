import json

from app.core.logging_config import logger
from app.schemas import UserCreate, UserUpdate
from app.services.user_service import UserService
from pydantic import ValidationError


class RedisSubscriber:
    def __init__(self, redis_client, user_service: UserService):
        self.redis_client = redis_client
        self.user_service = user_service

    async def listen_to_events(self, channel: str):
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)
            logger.info(f"Subscribed to {channel} channel.")

            async for message in pubsub.listen():
                logger.info(f"Received message: {message}")
                if message["type"] == "message":
                    event = json.loads(message["data"])
                    await self.handle_event(event)
        except Exception as e:
            logger.warning(f"Error in listening to events: {e}")

    async def handle_event(self, event: dict):
        event_type = event["event_type"]
        event_data = event["payload"]

        # Filter valid fields based on the schema
        def filter_valid_fields(data_dict, schema):
            return {
                key: value
                for key, value in data_dict.items()
                if key in schema.model_fields
            }

        try:
            if event_type == "create":
                # Filter and validate for UserCreate
                filtered_data = filter_valid_fields(event_data, UserCreate)
                user_data = UserCreate.model_validate(filtered_data)
                await self.user_service.create(user_data)
            elif event_type == "update":
                # Filter and validate for UserUpdate
                filtered_data = filter_valid_fields(event_data, UserUpdate)
                user_data = UserUpdate.model_validate(filtered_data)
                await self.user_service.update(user_data)
            elif event_type == "delete":
                # Directly use the `id` for delete
                user_id = event_data.get("id")
                if user_id:
                    await self.user_service.delete(user_id)
                else:
                    raise ValueError("Delete event must include 'id' in payload")
            else:
                raise ValueError(f"Unsupported event type: {event_type}")
        except ValidationError as e:
            # Log validation errors
            logger.error(f"Validation error for event {event_type}: {e}")
            raise
