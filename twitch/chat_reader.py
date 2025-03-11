from twitch.base import TwitchAPI
from utils.utils import setup_logging, save_json, load_json, get_timestamp
from config.config import Config
import asyncio
import logging
import os
import re
import websockets
from pathlib import Path
import sys

# Add the parent directory of the current file to the system path
sys.path.append(str(Path(__file__).resolve().parent))


setup_logging()


class TwitchChatReader:
    """Class to read and save Twitch chat messages"""

    def __init__(self, channel=None):
        """Initialize the Twitch chat reader"""
        self.channel = channel or Config.TWITCH_CHANNEL
        self.nickname = "justinfan12345"  # Anonymous connection
        self.irc_url = Config.TWITCH_IRC_URL

        # Set fixed output file in data/chat_logs folder
        self.output_file = f"data/chat_logs/recorded_chat_{get_timestamp()}.json"
        self.messages = {}
        self.running = False
        self.websocket = None
        self.message_count = 0 # Number of messages read
        self.batch_size = 250  # Save every 250 messages

        # Create chat_logs directory if it doesn't exist
        os.makedirs("data/chat_logs", exist_ok=True)

        # Load existing messages if the file exists
        existing_data = load_json(self.output_file)
        if existing_data:
            # Clean up any existing messages with trailing characters
            cleaned_data = {}
            for username, message in existing_data.items():
                cleaned_data[username] = message.rstrip(
                    '\r\n ') if isinstance(message, str) else message

            self.messages = cleaned_data
            logging.info(
                f"Loaded and cleaned {len(self.messages)} existing messages")

        # Save the cleaned messages back to the file
        if existing_data and self.messages != existing_data:
            self.save_messages()
            logging.info("Saved cleaned messages to file")

    async def connect(self):
        """Connect to Twitch IRC WebSocket"""
        try:
            self.websocket = await websockets.connect(self.irc_url)
            logging.info(
                f"Connected to Twitch IRC for channel #{self.channel}")

            # Anonymous authentication
            await self.websocket.send(f"PASS SCHMOOPIIE\r\n")
            await self.websocket.send(f"NICK {self.nickname}\r\n")
            await self.websocket.send(f"USER {self.nickname} 8 * :{self.nickname}\r\n")

            # Request capabilities
            await self.websocket.send("CAP REQ :twitch.tv/commands twitch.tv/tags\r\n")

            # Join the channel
            await self.websocket.send(f"JOIN #{self.channel}\r\n")

            return True
        except Exception as e:
            logging.error(f"Error connecting to Twitch IRC: {e}")
            return False

    async def read_messages(self):
        """Read and process messages from the WebSocket"""
        if not self.websocket:
            logging.error("WebSocket connection not established")
            return

        self.running = True
        try:
            while self.running:
                message = await self.websocket.recv()
                if "PING" in message:
                    await self.websocket.send("PONG :tmi.twitch.tv\r\n")
                    continue

                self.process_message(message)
        except websockets.exceptions.ConnectionClosed:
            logging.warning("WebSocket connection closed")
        except Exception as e:
            logging.error(f"Error reading messages: {e}")
        finally:
            self.running = False

    def process_message(self, message):
        """Process and save a chat message"""
        # Check if it's a PRIVMSG (chat message)
        if "PRIVMSG" not in message:
            return

        try:
            # Extract username and message text using regex
            username_match = re.search(r"display-name=([^;]+)", message)
            message_match = re.search(r"PRIVMSG #\w+ :(.+)", message)

            if username_match and message_match:
                username = username_match.group(1)
                msg_text = message_match.group(1)

                # If username is empty, try to extract from a different pattern
                if not username:
                    alt_username_match = re.search(r":(\w+)!", message)
                    if alt_username_match:
                        username = alt_username_match.group(1)

                # Save the message - keeping only the most recent message per user
                if username and msg_text:
                    # Strip trailing whitespace, carriage returns, and newlines
                    msg_text = msg_text.rstrip('\r\n ')

                    self.messages[username] = msg_text
                    logging.debug(f"{username}: {msg_text}")

                    # Increment message count
                    self.message_count += 1

                    # Save to JSON in batches
                    if self.message_count % self.batch_size == 0:
                        self.save_messages()
                        logging.info(
                            f"Saved batch of {self.batch_size} messages. Total messages: {len(self.messages)}")
        except Exception as e:
            logging.error(f"Error processing message: {e}")

    def save_messages(self):
        """Save messages to a JSON file"""
        try:
            save_json(self.messages, self.output_file)
        except Exception as e:
            logging.error(f"Error saving to {self.output_file}: {e}")

    async def start(self):
        """Start reading chat messages"""
        connected = await self.connect()
        if connected:
            await self.read_messages()

    async def stop(self):
        """Stop reading chat messages"""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logging.info("WebSocket connection closed")

        # Save messages before stopping
        self.save_messages()


async def main():
    """Main function to run the chat reader"""
    # Get channel name from command line arguments if provided
    import sys
    channel = sys.argv[1] if len(sys.argv) > 1 else Config.TWITCH_CHANNEL

    # Check if the channel is valid
    twitch_api = TwitchAPI()
    user = twitch_api.get_user_by_login(channel)
    if not user:
        logging.error(f"Channel '{channel}' not found")
        return

    # Check if the channel is live
    stream = twitch_api.get_stream(username=channel)
    if not stream:
        logging.warning(
            f"Channel '{channel}' is not live. Reading chat anyway.")
    else:
        logging.info(
            f"Channel '{channel}' is live: {stream.get('title', 'No title')}")

    # Start the chat reader
    chat_reader = TwitchChatReader(channel=channel)
    try:
        await chat_reader.start()
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Stopping chat reader.")
    finally:
        await chat_reader.stop()

if __name__ == "__main__":
    asyncio.run(main())
