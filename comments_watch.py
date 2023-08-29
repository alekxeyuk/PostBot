import gc
import signal

import socketio
from colorama import init
from termcolor import colored


init()


class WsBot:
    def __init__(self, url: str) -> None:
        signal.signal(signal.SIGINT, self.__handler)

        self.url = url
        self.sio = socketio.Client()

    def start(self) -> None:
        self.sio.register_namespace(SystemNamespace('/', self))
        self.sio.connect(self.url, transports="websocket")
        self.sio.wait()

    def __handler(self, signum, frame) -> int:
        print(colored('Shut Down', 'red'))
        self.sio.disconnect()
        gc.collect()
        return 0

    def new_comment_published(self, message: dict) -> None:
        def process(message: dict) -> None:
            post_id = message['content']['id']
            cmnt_id = message['comment_id']
            cmnt_user = message['user']['name']
            cmnt_text = message['text'] or 'ничего'
            cmnt_media = [i['data'] for i in message['media'] if i['type'] == 'image']
            cmnt_title = message['content']['title']
            print(colored(cmnt_user, 'cyan', 'on_grey'), f'{"Написал" if message["type"] != "comment_edited" else "Отредачил на"}=', colored(cmnt_text, 'green', 'on_grey'), '/!В пост с названием=', colored(cmnt_title, 'yellow', 'on_grey'), colored(post_id, 'red', 'on_grey'), '/!Получив id комментария=', colored(cmnt_id, 'red', 'on_grey'), colored(repr(cmnt_media), 'blue', 'on_grey'))
            del message, post_id, cmnt_id, cmnt_user, cmnt_text, cmnt_media, cmnt_title
        self.sio.start_background_task(process, message)


class SystemNamespace(socketio.ClientNamespace):
    def __init__(self, namespace: str, bot: WsBot):
        super().__init__(namespace=namespace)
        self.bot = bot

    def on_connect(self) -> None:
        print(colored("Websocket Launched!", 'green', 'on_grey'))
        self.emit("subscribe", {"channel": "live:private"})

    def on_disconnect(self) -> None:
        print(colored("Websocket Closed!", 'red', 'on_grey'))

    def on_event(self, data: dict) -> None:
        if data['data']['type'] in ('comment_add', 'comment_edited'):
            self.bot.new_comment_published(data['data'])


def main():
    print("Запуск Бота")
    WsBot("wss://ws-sio.dtf.ru").start()


if __name__ == '__main__':
    main()
