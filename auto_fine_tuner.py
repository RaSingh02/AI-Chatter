import asyncio
from twitch.base import TwitchBase
from chat_reader import TwitchChatReader
from dataset_formatter import format_dataset
from model_fine_tuner import train_model


class AutoFineTuner(TwitchBase):
    def __init__(self):
        super().__init__()
        self.chat_reader = TwitchChatReader()
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            if self.check_stream_status():
                self.chat_reader.clear_messages()
                await self.chat_reader.start()

                while self.check_stream_status():
                    await asyncio.sleep(60)

                await self.chat_reader.stop()

                if self.chat_reader.messages:
                    format_dataset()
                    train_model()

            await asyncio.sleep(300)

    async def stop(self):
        self.running = False
        await self.chat_reader.stop()


if __name__ == '__main__':
    tuner = AutoFineTuner()
    asyncio.run(tuner.start())
