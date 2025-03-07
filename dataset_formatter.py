from utils import load_json, save_json


def format_dataset():
    messages = load_json('recorded_chat.json')
    if messages:
        formatted_data = [message.split(': ', 1)[1] for message in messages]
        save_json(formatted_data, 'formatted_dataset.json')


if __name__ == '__main__':
    format_dataset()
