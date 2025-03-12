import datetime as dt
import logging
import json


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def get_timestamp():
    """Get a timestamp string suitable for filenames"""
    return dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


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
