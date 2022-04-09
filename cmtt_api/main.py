from requests_toolbelt import sessions


class CMTTApiClient:
    def __init__(self, site: str = 'dtf.ru', api_v: str = '1.9') -> None:
        self.site = site
        self.sess = sessions.BaseUrlSession(
            base_url=f'https://api.{site}/v{api_v}/'
        )

    def get_user_info(self, user_id: int) -> dict:
        return self.sess.get('locate', params={'url': f'https://{self.site}/u/{user_id}'}).json().get('result', {})

    def get_post_info(self, post_id: int) -> dict:
        return self.sess.get('locate', params={'url': f'https://{self.site}/{post_id}'}).json().get('result', {})
