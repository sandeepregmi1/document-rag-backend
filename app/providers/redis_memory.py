import redis


class RedisMemory:

    def __init__(
        self,
        host: str,
        port: int,
    ):

        self.client = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
        )

    def ping(self):

        return self.client.ping()