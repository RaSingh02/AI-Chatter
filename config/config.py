import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    TWITCH_ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    TWITCH_REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')
    TWITCH_CLIENT_ID = os.getenv('CLIENT_ID')
    TWITCH_CHANNEL = os.getenv('CHANNEL')
    TWITCH_IRC_URL = 'wss://irc-ws.chat.twitch.tv:443'
    MODEL_PATH = 'fine_tuned_model'
    BASE_MODEL = os.getenv('MODEL') | 'unsloth/DeepSeek-R1-Distill-Llama-8B'

    # Fine-tuning configs
    MAX_SEQ_LENGTH = 2048
    LOAD_IN_4BIT = True
    LORA_RANK = 16
    LORA_ALPHA = 16
    BATCH_SIZE = 2
    GRADIENT_ACCUMULATION_STEPS = 4
    WARMUP_STEPS = 5
    LEARNING_RATE = 2e-4
    WEIGHT_DECAY = 0.01
    TRAINING_STEPS = 500  # Minimum recommended steps
