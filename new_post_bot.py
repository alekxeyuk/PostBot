import gc
import signal

import socketio
from colorama import init
from termcolor import colored

from cmtt_api import CMTTApiClient
from redis_api import RedisClient
from telegram_api import ApiClient

init()


class WsBot:
    def __init__(self, url: str) -> None:
        signal.signal(signal.SIGINT, self.__handler)

        self.client = ApiClient()
        self.redis = RedisClient()
        self.dtf_api = CMTTApiClient('dtf.ru', '1.9')
        self.url = url

        self.sio = socketio.Client()

    def start(self) -> None:
        self.sio.register_namespace(SystemNamespace('/', self))
        self.sio.connect(self.url, transports="websocket")
        self.sio.on('new_entry_published', self.new_entry_published)
        self.sio.wait()

    def __handler(self, signum, frame) -> int:
        print(colored('Shut Down', 'red'))
        self.sio.disconnect()
        gc.collect()
        return 0

    def get_or_set_user(self, user_id: int) -> dict:
        if user := self.redis.get_user_info(user_id):
            return user
        user = self.dtf_api.get_user_info(user_id)
        user_data = {'type': user['type'], 'name': user['data']['name']}
        self.redis.set_user_info(user_id, mapping=user_data)
        return user_data

    def new_entry_published(self, message: dict) -> None:
        def process(message: dict) -> None:
            print(message)
            subsite_id, content_id = message['subsite_id'], message['content_id']
            user_info = self.get_or_set_user(subsite_id)
            print(user_info)
            self.client.new_channel_message(
                text=f"[Запись](https://dtf.ru/{content_id}) в {'подсайте' if user_info['type'] == 'section' else 'блоге'} [{user_info['name']}](https://dtf.ru/u/{subsite_id})\nОригинал: https://dtf.ru/{content_id}")
        self.sio.start_background_task(process, message)


class SystemNamespace(socketio.ClientNamespace):
    def __init__(self, namespace: str, bot: WsBot):
        super().__init__(namespace=namespace)
        self.bot = bot

    def on_connect(self) -> None:
        print(colored("Websocket Launched!", 'green', 'on_grey'))
        self.emit("subscribe", {"channel": "system"})

    def on_disconnect(self) -> None:
        print(colored("Websocket Closed!", 'red', 'on_grey'))

    def on_event(self, data: dict) -> None:
        if data['data']['type'] == 'new_entry_published' and 'original_subsite_id' not in data['data']:
            self.bot.new_entry_published(data['data'])


def main():
    print("Запуск Бота")
    WsBot("wss://ws-sio.dtf.ru").start()


if __name__ == '__main__':
    main()
