import requests
import time
from config import Config
from utils import get_twitch_access_token


def is_streaming(access_token):
    url = f'https://api.twitch.tv/helix/streams?user_login={Config.TWITCH_CHANNEL}'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Client-ID': Config.TWITCH_CLIENT_ID
    }
    response = requests.get(url, headers=headers)
    return len(response.json()['data']) > 0


if __name__ == '__main__':
    while True:
        token = get_twitch_access_token()
        if is_streaming(token):
            print('Streamer is live! Starting the bot...')
        else:
            print('Streamer is offline.')
        time.sleep(600)
