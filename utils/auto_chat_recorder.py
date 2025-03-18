import asyncio
import logging
import os
from typing import Coroutine

from config.config import Config
from utils.dataset_formatter import format_dataset
from twitch.chat_reader import TwitchChatReader
from utils.utils import setup_logging, get_timestamp

# Create logs directory for the live stream detector
os.makedirs("logs/live_stream_detector", exist_ok=True)

# Setup logging
setup_logging()
logger = logging.getLogger("auto_chat_recorder")
logger.setLevel(logging.INFO)

# Add file handler to log to a file
log_file = f"logs/auto_chat_recorder_{get_timestamp()}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


class AutoChatRecorder:
    """Class to record Twitch chat logs"""

    def __init__(self, channel=None):
        """Initialize the chat recorder"""
        self.channel = channel or Config.TWITCH_CHANNEL
        self.chat_reader = None

    async def start(self):
        """Start recording chat"""
        logger.info(f"Starting chat recording for channel '{self.channel}'")

        self.chat_reader = TwitchChatReader(channel=self.channel)

        try:
            await self.chat_reader.start()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Stopping chat recorder.")
        finally:
            if self.chat_reader:
                await self.chat_reader.stop()
                logger.info("Chat recorder stopped")
                # Format the dataset
                logger.info("Formatting chat logs into dataset")
                try:
                    if isinstance(format_dataset, Coroutine):
                        await format_dataset()
                    else:
                        format_dataset()
                    logger.info("Dataset formatting complete")
                except Exception as e:
                    logger.error(f"Error formatting dataset: {e}")
                    raise  # Re-raise to ensure we see the full error


async def main():
    """Main function to run the chat recorder"""
    recorder = AutoChatRecorder(channel=Config.TWITCH_CHANNEL)
    await recorder.start()


if __name__ == "__main__":
    asyncio.run(main())
