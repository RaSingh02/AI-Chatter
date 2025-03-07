import datetime
import logging
import json
import requests
from config import Config


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_timestamp():
    return datetime.datetime.now().strftime('%H:%M:%S')


def get_log_colors():
    return {
        'INFO': '#d4d4d4',
        'ERROR': '#ff6b6b',
        'SUCCESS': '#6bff6b',
        'WARNING': '#ffd700'
    }


def save_json(data, filename):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
        logging.info(f'Saved data to {filename}')
    except Exception as e:
        logging.error(f'Error saving to {filename}: {e}')


def load_json(filename):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f'Error loading {filename}: {e}')
        return None


def get_twitch_access_token():
    url = 'https://id.twitch.tv/oauth2/token'
    params = {
        'client_id': Config.TWITCH_CLIENT_ID,
        'client_secret': Config.TWITCH_ACCESS_TOKEN,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, params=params)
    return response.json()['access_token']
