from functools import singledispatchmethod
import redis
from conf import REDIS_URL


class RedisClient:
    def __init__(self) -> None:
        self.redis_url = REDIS_URL
        self.r_c = redis.from_url(self.redis_url, decode_responses=True)

        self.user_info_keys = ('type', 'name')

    def get_user_info(self, user_id: int) -> dict:
        response = self.r_c.hmget(f'u:{user_id}', keys=self.user_info_keys)
        if all(response):
            return dict(zip(self.user_info_keys, response))
        return {}

    @singledispatchmethod
    def set_user_info(self, user_id: int, *args, **kwargs):
        raise NotImplementedError

    @set_user_info.register
    def _args(self, user_id: int, user_type: str, user_name: str):
        self.r_c.hset(f'u:{user_id}', mapping=dict(zip(self.user_info_keys, (user_type, user_name))))

    @set_user_info.register
    def _mapping(self, user_id: int, mapping: dict):
        self.r_c.hset(f'u:{user_id}', mapping=mapping)


if __name__ == "__main__":
    client = RedisClient()
    client.set_user_info(72070, 'section', 'Мемы')
    _ = client.get_user_info(72070)
    print(_)
