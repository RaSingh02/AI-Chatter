import asyncio
import logging
import os
from datetime import datetime

from config.config import Config
from utils.utils import setup_logging, save_json, load_json
from twitch.base import TwitchAPI

# Create logs directory for the live stream detector
os.makedirs("logs/live_stream_detector", exist_ok=True)

# Setup logging with file handler for live stream detector
setup_logging()
logger = logging.getLogger("live_stream_detector")
logger.setLevel(logging.INFO)

# Add file handler to log to a file
log_file = f"logs/live_stream_detector/detector_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


class LiveStreamDetector:
    """Class to detect when a Twitch streamer goes live"""

    def __init__(self, channel=None, check_interval=6000, callback=None):
        """Initialize the live stream detector"""
        self.channel = channel or Config.TWITCH_CHANNEL
        self.check_interval = check_interval  # seconds
        self.callback = callback
        self.twitch_api = TwitchAPI()
        self.is_live = False
        self.stream_info = None
        self.running = False
        self.status_file = f"logs/live_stream_detector/stream_status_{self.channel}.json"

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.status_file), exist_ok=True)

        # Load previous status if exists
        status_data = load_json(self.status_file)
        if status_data:
            self.is_live = status_data.get("is_live", False)
            self.stream_info = status_data.get("stream_info", None)

    async def check_stream_status(self):
        """Check if the streamer is live"""
        # Get user information
        user = self.twitch_api.get_user_by_login(self.channel)
        if not user:
            logger.error(f"Channel '{self.channel}' not found")
            return False, None

        # Check stream status
        stream = self.twitch_api.get_stream(user_id=user["id"])

        # Return stream status and info
        return bool(stream), stream

    def save_status(self):
        """Save the current stream status"""
        status_data = {
            "is_live": self.is_live,
            "stream_info": self.stream_info,
            "last_updated": datetime.now().isoformat()
        }
        save_json(status_data, self.status_file)

    async def monitor(self):
        """Monitor the stream status continuously"""
        self.running = True
        previous_status = self.is_live

        logger.info(f"Starting stream monitor for channel '{self.channel}'")

        while self.running:
            try:
                is_live, stream_info = await self.check_stream_status()

                # Update status
                self.is_live = is_live
                self.stream_info = stream_info

                # Log status changes
                if is_live != previous_status:
                    if is_live:
                        logger.info(
                            f"🔴 {self.channel} is now LIVE: {stream_info.get('title', 'No title')}")
                        # Execute callback if provided
                        if self.callback:
                            await self.callback(self.channel, True, stream_info)
                    else:
                        logger.info(f"⚫ {self.channel} is now OFFLINE")
                        # Execute callback if provided
                        if self.callback:
                            await self.callback(self.channel, False, None)

                # Save current status
                self.save_status()

                # Update previous status
                previous_status = is_live

                # Wait before next check
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error monitoring stream: {e}")
                await asyncio.sleep(self.check_interval)

    async def start(self):
        """Start monitoring"""
        await self.monitor()

    async def stop(self):
        """Stop monitoring"""
        self.running = False
        logger.info(f"Stopped monitoring channel '{self.channel}'")


async def stream_notification_callback(channel, is_live, stream_info):
    """Example callback function when stream status changes"""
    if is_live:
        print(f"\n{'='*50}")
        print(f"🔴 {channel} IS NOW LIVE!")
        print(f"Title: {stream_info.get('title', 'No title')}")
        print(f"Game: {stream_info.get('game_name', 'Unknown game')}")
        print(f"Viewers: {stream_info.get('viewer_count', 0)}")
        print(f"Started at: {stream_info.get('started_at', 'Unknown')}")
        print(f"{'='*50}\n")
    else:
        print(f"\n{'='*50}")
        print(f"⚫ {channel} IS NOW OFFLINE")
        print(f"{'='*50}\n")


async def main():
    """Main function to run the stream detector"""

    # Create and start the detector
    detector = LiveStreamDetector(
        Config.TWITCH_CHANNEL, callback=stream_notification_callback)

    try:
        await detector.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping detector.")
    finally:
        await detector.stop()

if __name__ == "__main__":
    asyncio.run(main())
