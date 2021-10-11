from requests_toolbelt import sessions
from conf import TELEGRAM_URL, TELEGRAM_CHANNEL


class ApiClient:
    def __init__(self) -> None:
        self.sess = sessions.BaseUrlSession(
            base_url=TELEGRAM_URL
        )

    def new_channel_message(self, chat_id: str = TELEGRAM_CHANNEL, text: str = '') -> dict:
        return self.sess.post('sendMessage', data={'chat_id': chat_id, 'text': text, 'parse_mode': 'Markdown'}).json()
