import asyncio
import logging
from twitchio.ext import commands
from transformers import DeepseekR1Model, DeepseekR1Tokenizer
from config import Config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=Config.TWITCH_ACCESS_TOKEN,
            client_id=Config.TWITCH_CLIENT_ID,
            prefix='!',
            initial_channels=[Config.TWITCH_CHANNEL]
        )
        self.model = DeepseekR1Model.from_pretrained(Config.MODEL_PATH)
        self.tokenizer = DeepseekR1Tokenizer.from_pretrained(Config.MODEL_PATH)

    async def event_ready(self):
        logging.info(f'Bot is ready | {self.nick}')

    async def event_message(self, message):
        if message.echo:
            return

        try:
            # Generate response using the model
            inputs = self.tokenizer(message.content, return_tensors="pt")
            outputs = self.model.generate(**inputs, max_length=100)
            response = self.tokenizer.decode(
                outputs[0], skip_special_tokens=True)

            # Send response
            await message.channel.send(response)
        except Exception as e:
            logging.error(f"Error processing message: {e}")


async def main():
    bot = TwitchBot()
    await bot.start()

if __name__ == '__main__':
    asyncio.run(main())
