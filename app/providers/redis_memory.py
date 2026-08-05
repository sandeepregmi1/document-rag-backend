import json


class RedisMemory:
    """
    Wrapper around Redis for storing
    conversation history.
    """

    def __init__(
        self,
        host: str,
        port: int,
    ) -> None:

        import redis

        self.client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    def ping(self) -> bool:
        """
        Check Redis connection.
        """
        return self.client.ping()

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:
        """
        Save one chat message.
        """

        message = {
            "role": role,
            "content": content,
        }

        self.client.rpush(
            session_id,
            json.dumps(message),
        )

    def load_history(
        self,
        session_id: str,
    ) -> list[dict]:
        """
        Load complete conversation.
        """

        messages = self.client.lrange(
            session_id,
            0,
            -1,
        )

        return [
            json.loads(message)
            for message in messages
        ]

    def clear_history(
        self,
        session_id: str,
    ) -> None:
        """
        Delete a conversation.
        """

        self.client.delete(session_id)