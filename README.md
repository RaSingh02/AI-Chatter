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