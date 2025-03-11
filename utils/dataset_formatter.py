from utils.utils import load_json, save_json, get_timestamp
import re

def clean_message(message):
    # Remove URLs
    message = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', message)
    
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
    messages = load_json(f'data/chat_logs/recorded_chat_{get_timestamp()}.json')
    formatted_data = []
    
    # messages is a dictionary where keys are usernames and values are dictionaries with 'message' and 'timestamp'
    for username, message_data in messages.items():
        try:
            # Extract the message text
            message = message_data['message']
            cleaned_message = clean_message(message)
            if cleaned_message:  # Only add non-empty messages
                formatted_data.append(cleaned_message)
        except Exception as e:
            print(f"Error processing message from {username}: {message_data}")
            print(f"Error details: {str(e)}")
            continue
            
    save_json(formatted_data, f'data/formatted_logs/dataset_{get_timestamp()}.json')


if __name__ == '__main__':
    format_dataset()
