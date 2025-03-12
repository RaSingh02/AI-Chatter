import asyncio
import logging
import os

from config.config import Config
from utils.live_stream_detector import LiveStreamDetector
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
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


class AutoChatRecorder:
    """Class to automatically record chat logs when a streamer goes live"""
    
    def __init__(self, channel=None, check_interval=60):
        """Initialize the auto chat recorder"""
        self.channel = channel or Config.TWITCH_CHANNEL
        self.check_interval = check_interval  # seconds between checks
        self.chat_reader = None
        self.detector = None
        self.recording = False
        self.current_session_file = None
        
    async def stream_status_callback(self, channel, is_live, stream_info):
        """Callback function when stream status changes"""
        if is_live and not self.recording:
            logger.info(f"🔴 {channel} is now LIVE - Starting chat recording")
            # Start the chat reader
            self.chat_reader = TwitchChatReader(channel=channel)
            # Store the current session file path
            self.current_session_file = self.chat_reader.output_file
            # Start recording in a separate task
            asyncio.create_task(self.chat_reader.start())
            self.recording = True
        elif not is_live and self.recording:
            logger.info(f"⚫ {channel} is now OFFLINE - Stopping chat recording")
            # Stop the chat reader
            if self.chat_reader:
                await self.chat_reader.stop()
                self.chat_reader = None
                self.recording = False
                # Format the dataset
                logger.info("Formatting chat logs into dataset")
                format_dataset()
                logger.info("Dataset formatting complete")
    
    async def start(self):
        """Start the auto chat recorder"""
        logger.info(f"Starting auto chat recorder for channel '{self.channel}'")
        
        # Create the detector with our callback
        self.detector = LiveStreamDetector(
            channel=self.channel,
            check_interval=self.check_interval,
            callback=self.stream_status_callback
        )
        
        try:
            await self.detector.start()
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Stopping auto chat recorder.")
        finally:
            if self.recording and self.chat_reader:
                await self.chat_reader.stop()
            await self.detector.stop()
            logger.info("Auto chat recorder stopped")


async def main():
    """Main function to run the auto chat recorder"""
    recorder = AutoChatRecorder(
        channel=Config.TWITCH_CHANNEL,
        check_interval=600  # Check every 10 minutes
    )
    
    await recorder.start()


if __name__ == "__main__":
    asyncio.run(main()) 