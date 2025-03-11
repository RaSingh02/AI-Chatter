# Twitch Chat Bot with Deepseek R1 Fine-Tuning

This project implements a Twitch chat bot that fine-tunes a Deepseek R1 model using live Twitch chat messages from the streamer Squeex. The bot can post messages and respond to chat interactions.

## Requirements
- Python 3.7+
- Install the required packages:
```bash
pip install -r requirements.txt
```

## Scripts
1. **twitch_chat_reader.py**: Connects to Twitch chat and records messages.
2. **dataset_formatter.py**: Formats recorded chat messages into a dataset for fine-tuning.
3. **model_fine_tuner.py**: Fine-tunes the Deepseek R1 model using the formatted dataset.
4. **twitch_bot.py**: The bot that uses the fine-tuned model to interact in Twitch chat.
5. **live_stream_detector.py**: Detects when the streamer is live and manages the bot's operation.

## Usage
1. Set your Twitch OAuth token, client ID, and client secret in the respective scripts.
2. Run `twitch_chat_reader.py` to start recording chat messages.
3. Run `dataset_formatter.py` to format the recorded messages.
4. Run `model_fine_tuner.py` to fine-tune the model.
5. Run `live_stream_detector.py` to start the bot when the streamer is live.

## Notes
- Ensure you have the necessary permissions and follow Twitch's guidelines when using the API and interacting in chat.

# Twitch Chat Reader and Live Stream Detector

This project provides tools to read Twitch chat messages and detect when a streamer goes live. It consists of several scripts:

- `chat_reader.py`: Reads chat messages from a Twitch channel and saves them to a JSON file
- `live_stream_detector.py`: Detects when a Twitch streamer goes live or offline
- `twitch/base.py`: Base functionality for Twitch API interactions

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the root directory with your Twitch API credentials:
   ```
   ACCESS_TOKEN=your_access_token
   REFRESH_TOKEN=your_refresh_token
   CLIENT_ID=your_client_id
   ```

   You can obtain these credentials by creating a Twitch Developer Application at [dev.twitch.tv/console/apps](https://dev.twitch.tv/console/apps).

## Usage

### Chat Reader

The chat reader connects to a Twitch channel's chat and saves messages to a JSON file in the format:
```
{
  "username1": "message1",
  "username2": "message2"
}
```

The chat reader stores only the most recent message from each user and saves them in batches to `chat_logs/recorded_chat.json`.

To start the chat reader:
```
python chat_reader.py [channel_name]
```

If no channel name is provided, it will use the default channel specified in `config.py`.

### Live Stream Detector

The live stream detector checks if a Twitch channel is currently live and notifies you when the status changes.

To start the live stream detector:
```
python live_stream_detector.py [channel_name]
```

If no channel name is provided, it will use the default channel specified in `config.py`.

## Configuration

You can modify settings in the `config.py` file:

- `TWITCH_CHANNEL`: Default Twitch channel to monitor
- `TWITCH_IRC_URL`: Twitch IRC WebSocket URL
- Other configuration options for authentication and API requests

## Files

- `chat_logs/recorded_chat.json`: Where chat messages are stored
- `stream_status_{channel}.json`: Contains the current stream status for a channel

## Notes

- The chat reader uses an anonymous connection, so it doesn't require authentication to read chat messages
- The live stream detector requires Twitch API credentials to check stream status
- Both scripts can be stopped with a keyboard interrupt (Ctrl+C) 