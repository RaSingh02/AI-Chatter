import logging
from pathlib import Path
from utils.utils import load_json, save_json
import re


def clean_message(message):
    # Remove URLs
    message = re.sub(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', message)

    # Remove Unicode escape sequences like \ud83e\udd75
    message = re.sub(r'\\u[0-9a-fA-F]{4}(?:\\u[0-9a-fA-F]{4})?', '', message)

    # Remove any remaining backslash sequences
    message = re.sub(r'\\[a-zA-Z0-9]{2,}', '', message)

    # Strip extra whitespace
    message = message.strip()

    # If after cleaning the message is empty, return None
    return message if message else None

# Load in the chat logs and format them into a dataset, removing the username and just leaving the message
# Example: "david_kapp": "LUL LUL LUL"
# Becomes: "LUL LUL LUL"


def format_dataset():
    # Read in all JSONs in the chat_logs directory
    messages = {}
    for file in Path('data/chat_logs').rglob('*.json'):
        try:
            data = load_json(file)
            messages.update(data)  # Fixed the line break here
        except Exception as e:
            logging.error(f"Failed to load {file}: {str(e)}")
            continue

    logging.info(f"Loaded {len(messages)} messages")

    formatted_data = []

    # messages is a dictionary where keys are usernames and values are dictionaries with 'message' and 'timestamp'
    for username, message_data in messages.items():
        try:
            # Extract the message text
            if isinstance(message_data, str):
                # Handle case where message is directly stored as string
                message = message_data
            else:
                # Handle case where message is in a dictionary
                message = message_data['message']

            cleaned_message = clean_message(message)
            if cleaned_message:  # Only add non-empty messages
                formatted_data.append(cleaned_message)
        except Exception as e:
            logging.error(
                f"Error processing message from {username}: {str(e)}")
            continue

    save_json(formatted_data,
              f'data/formatted_logs/dataset.json')


if __name__ == '__main__':
    format_dataset()
