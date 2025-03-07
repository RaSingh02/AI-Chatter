import asyncio
import logging
import websockets
import time
from config import Config
from utils import setup_logging, save_json
from twitch.base import TwitchBase

setup_logging()


class TwitchChatReader(TwitchBase):
    def __init__(self):
        super().__init__()
        self.websocket = None
        self.messages = []
        self.last_save = time.time()
        self.save_interval = 60
        self.running = False

    async def connect(self):
        try:
            self.websocket = await websockets.connect(Config.TWITCH_IRC_URL)
            await self.websocket.send(f'PASS oauth:{self.refresh_token()}')
            await self.websocket.send('NICK PlusTwoTracker')
            await self.websocket.send(f'JOIN #{Config.TWITCH_CHANNEL}')
            logging.info(f'Connected to {Config.TWITCH_CHANNEL}\'s chat')
            return True
        except Exception as e:
            logging.error(f'Connection error: {e}')
            return False

    async def stop(self):
        self.running = False
        if self.websocket:
            await self.websocket.close()

    def clear_messages(self):
        self.messages = []

    async def save_messages(self):
        if self.messages:
            save_json(self.messages, 'recorded_chat.json')

    async def read_chat(self):
        if not await self.connect():
            return

        self.running = True
        try:
            while self.running:
                message = await self.websocket.recv()
                if message.startswith('PING'):
                    await self.websocket.send('PONG :tmi.twitch.tv')
                    continue

                if 'PRIVMSG' in message:
                    username = message.split('!')[0][1:]
                    content = message.split('PRIVMSG')[
                        1].split(':', 1)[1].strip()

                    chat_message = f'{username}: {content}'
                    self.messages.append(chat_message)
                    logging.info(chat_message)

                    current_time = time.time()
                    if current_time - self.last_save >= self.save_interval:
                        await self.save_messages()
                        self.last_save = current_time

        except websockets.exceptions.ConnectionClosed:
            logging.error('Connection to Twitch chat closed')
        except Exception as e:
            logging.error(f'Error reading chat: {e}')
        finally:
            await self.save_messages()
            if self.websocket:
                await self.websocket.close()


async def main():
    reader = TwitchChatReader()
    await reader.read_chat()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info('Chat reader stopped by user')
