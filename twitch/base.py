import logging
from abc import ABC, abstractmethod
import requests
from config import Config
from utils import setup_logging

setup_logging()


class TwitchBase(ABC):
    def __init__(self):
        self.access_token = None

    def refresh_token(self):
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': Config.TWITCH_CLIENT_ID,
            'client_secret': Config.TWITCH_ACCESS_TOKEN,
            'grant_type': 'client_credentials'
        }
        response = requests.post(url, params=params)
        self.access_token = response.json()['access_token']
        return self.access_token

    def check_stream_status(self):
        if not self.access_token:
            self.refresh_token()

        url = f'https://api.twitch.tv/helix/streams?user_login={Config.TWITCH_CHANNEL}'
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Client-ID': Config.TWITCH_CLIENT_ID
        }
        response = requests.get(url, headers=headers)
        return len(response.json()['data']) > 0

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
